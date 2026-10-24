"""
Shared chat logic used by BOTH interfaces (the command-line app.py and the
Streamlit web app). Keeping this in one place means any future change to
how retrieval or conversation handling works only needs to happen once,
and both interfaces automatically stay in sync.
"""

import json
from core.retriever import retrieve_context
from core.prompt_template import SYSTEM_PROMPT

try:
    from groq import RateLimitError
except ImportError:
    # Defensive fallback in case the installed groq version doesn't expose
    # this exact class -- treat rate limit errors as regular exceptions
    # instead of crashing on import.
    class RateLimitError(Exception):
        pass


def _estimate_tokens(text: str) -> int:
    """
    Rough token count estimate (~4 characters per token for English text).
    Not exact, but good enough to stay safely under the API's per-minute
    token limit without needing a dedicated tokenizer library.
    """
    return max(1, len(text) // 4)


def _trim_for_api(conversation: list, max_input_tokens: int = 4500) -> list:
    """
    Returns a TRIMMED COPY of the conversation for sending to the API --
    always keeps the system prompt (first message), then includes as many
    of the most recent messages as fit within max_input_tokens (estimated).

    This matters now that conversations persist across sessions instead
    of resetting each time: without trimming, a long-running conversation
    would eventually exceed Groq's free-tier tokens-per-minute limit and
    every further message would fail outright.

    Only what's SENT to the model is trimmed -- the full, untrimmed
    conversation is still kept in session/file storage so the user can
    scroll back through their entire chat history in the UI.
    """
    system_msg = conversation[0]
    budget = max_input_tokens - _estimate_tokens(system_msg["content"])

    kept = []
    for msg in reversed(conversation[1:]):
        cost = _estimate_tokens(msg["content"])
        if cost > budget:
            break
        kept.insert(0, msg)
        budget -= cost

    return [system_msg] + kept


def _build_retrieval_query(conversation: list, question: str) -> str:
    """
    Builds the text actually used to search the knowledge base. A short,
    vague follow-up question ("what year was it published?") often
    doesn't contain enough distinctive keywords on its own for semantic
    search to find the right entry -- so when there's a recent assistant
    answer, it's included alongside the new question, biasing retrieval
    toward whatever topic was just being discussed.

    This does NOT change what's sent to the LLM -- only what's used to
    search the database. The actual question sent to the model is always
    just the question itself.
    """
    for msg in reversed(conversation):
        if msg["role"] == "assistant":
            return f"{msg['content']}\n\n{question}"
    return question


def get_response(conversation: list, question: str, ask_fn) -> str:
    """
    Handles one full turn of the conversation:
    1. Adds the user's question to the conversation history
    2. Retrieves relevant knowledge base content, if any
    3. Builds a temporary augmented message for the API call (without
       permanently polluting the saved conversation history)
    4. Calls the LLM and returns its answer
    5. Saves the clean answer back into the conversation history

    `ask_fn` is the LLM client function to use (e.g. ask_cyberprep from
    llm_client_groq.py) -- passed in rather than imported directly, so
    this file doesn't need to care which backend (Groq or Ollama) is
    being used.

    If the API call fails, the user's question is removed from history
    again (rollback), and the exception is re-raised so the calling
    interface can display an appropriate error message.
    """
    conversation.append({"role": "user", "content": question})

    retrieval_query = _build_retrieval_query(conversation, question)
    context = retrieve_context(retrieval_query)

    # Trim what's sent to the API (not the saved conversation itself) so a
    # long, persisted conversation never exceeds the token-per-minute limit.
    trimmed = _trim_for_api(conversation)

    if context:
        augmented_question = f"{question}\n\n[Reference material:]\n{context}"
        api_messages = trimmed[:-1] + [
            {"role": "user", "content": augmented_question}
        ]
    else:
        api_messages = trimmed

    try:
        answer = ask_fn(api_messages)
    except Exception:
        conversation.pop()  # roll back the question since we never got an answer
        raise

    conversation.append({"role": "assistant", "content": answer})
    return answer


# Phrases that suggest the user wants every item from a previous list
# explained individually, rather than a single normal question.
_MULTI_TERM_TRIGGERS = [
    "explain each", "explain all", "explain every", "explain them all",
    "explain these terms", "explain each term", "explain each one",
    "describe each", "define each", "explain all of them",
    "explain all of these",
]


def _wants_multiple_explanations(question: str, conversation: list) -> bool:
    """
    Heuristic check: does this look like a request to explain every term
    from a list the assistant just gave? Requires at least one prior
    exchange to exist -- "explain each" only makes sense in reference to
    something already listed.
    """
    if len(conversation) < 3:  # system + at least one prior user/assistant pair
        return False
    lowered = question.lower()
    return any(trigger in lowered for trigger in _MULTI_TERM_TRIGGERS)


def _extract_term_list(conversation: list, ask_fn) -> list:
    """
    Asks the model to distill the list it just gave into a clean JSON
    array of term names. This is far more reliable than trying to
    regex-parse the model's free-form Markdown list, which varies in
    exact formatting from one answer to the next.

    Deliberately sends ONLY the single most recent assistant message (the
    list itself) rather than the whole conversation history. Sending the
    full history let the model get confused about WHICH list to extract
    from in a long conversation containing several lists or topics --
    picking the exact message removes that ambiguity entirely.
    """
    last_assistant_message = None
    for msg in reversed(conversation[:-1]):  # skip the "explain each" question just added
        if msg["role"] == "assistant":
            last_assistant_message = msg["content"]
            break

    if not last_assistant_message:
        return []

    extraction_request = [
        {
            "role": "system",
            "content": (
                "You extract term names from a numbered list of items. "
                "Respond with ONLY a JSON array of the term names, nothing "
                "else. No markdown formatting, no explanation, no code "
                'fence. Example: ["Firewall", "VPN", "DNS"]'
            ),
        },
        {
            "role": "user",
            "content": f"Extract the term names from this list:\n\n{last_assistant_message}",
        },
    ]
    raw = ask_fn(extraction_request)

    # The model sometimes wraps the JSON in a markdown code fence despite
    # instructions not to -- strip that defensively before parsing.
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        terms = json.loads(cleaned)
        if isinstance(terms, list) and terms:
            return [str(t) for t in terms]
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def explain_multiple_terms(
    conversation: list, question: str, ask_fn, on_progress=None
) -> str:
    """
    Handles "explain each/all of them" style requests by looping through
    each term INDIVIDUALLY -- giving every term the same fresh, focused
    quality as a standalone question, instead of asking the model to
    produce all explanations in one long response (which tends to
    degrade in quality and formatting partway through).

    Each term is asked as its own short, independent conversation (system
    prompt + "What is X?"), with its own knowledge base retrieval, exactly
    matching the pipeline already proven to work well for single terms.

    If a rate limit or other error interrupts the loop partway through,
    whatever was successfully completed so far is still returned, along
    with a clear note about what happened -- never silently losing
    completed work. (An earlier version of this function tried to
    proactively self-throttle with blocking sleeps to avoid ever hitting
    this error, but that caused the whole app to freeze unresponsively
    for long stretches under Streamlit's synchronous execution model --
    a stop-and-resume approach turned out to be more predictable and
    reliable in practice than a silent, possibly-very-long pause.)

    `on_progress`, if given, is called as on_progress(current, total, term)
    right before each term starts processing -- this lets the calling
    interface show live progress (e.g. updating a status label), without
    this file needing to know anything about Streamlit or any other UI.
    """
    conversation.append({"role": "user", "content": question})

    terms = _extract_term_list(conversation, ask_fn)

    if not terms:
        # Couldn't confidently extract a term list (e.g. there wasn't
        # actually a list in the recent conversation) -- fall back to the
        # normal single-response path instead of doing nothing.
        conversation.pop()
        return get_response(conversation, question, ask_fn)

    sections = []
    completed = 0

    for term in terms:
        if on_progress:
            on_progress(completed + 1, len(terms), term)

        term_question = f"What is {term}?"
        term_conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": term_question},
        ]

        context = retrieve_context(term)
        if context:
            term_conversation[-1]["content"] = (
                f"{term_question}\n\n[Reference material:]\n{context}"
            )

        try:
            answer = ask_fn(term_conversation)
        except RateLimitError:
            sections.append(
                f"---\n\n*Reached my request limit for this minute after "
                f"explaining {completed} of {len(terms)} terms. Ask me to "
                f"continue with the rest in a moment.*"
            )
            break
        except Exception as e:
            sections.append(
                f"---\n\n*Ran into an error after explaining {completed} "
                f"of {len(terms)} terms: {e}*"
            )
            break

        sections.append(f"### {completed + 1}. {term}\n\n{answer}")
        completed += 1

    combined_answer = "\n\n---\n\n".join(sections)
    conversation.append({"role": "assistant", "content": combined_answer})
    return combined_answer


def handle_user_message(
    conversation: list, question: str, ask_fn, on_progress=None
) -> str:
    """
    The single entry point both interfaces (app.py and streamlit_app.py)
    should call. Decides whether this question should be handled as a
    multi-term explanation request (looping per term, Option A) or routed
    through the normal single-turn RAG flow. `on_progress` is only ever
    used in the multi-term case -- a normal single question has nothing
    to report progress on.
    """
    if _wants_multiple_explanations(question, conversation):
        return explain_multiple_terms(conversation, question, ask_fn, on_progress)
    return get_response(conversation, question, ask_fn)
