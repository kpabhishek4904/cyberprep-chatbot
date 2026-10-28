"""
CyberPrep -- Phase 4 Web Interface

The browser-based version of the chatbot, built with Streamlit. This uses
the exact same logic as app.py (via core/chat_engine.py) -- only the
interface is different.

Run with:  streamlit run streamlit_app.py
(NOT "python streamlit_app.py" -- Streamlit needs its own launcher command)
"""

import os
import json
import random
import streamlit as st
import markdown as md_lib

# set_page_config() must be the very first Streamlit command to run, before
# ANYTHING else that touches st.* -- including st.secrets below, which
# Streamlit renders its own warning box for internally when no secrets.toml
# exists (as is expected locally). That internal render counts as "a
# Streamlit command," so it has to come after this line, not before.
st.set_page_config(page_title="CyberPrep", page_icon="🛡︎", layout="wide")

# --- Deployment setup: bridge Streamlit Cloud secrets into the environment ---
# Locally, the GROQ_API_KEY comes from a .env file (loaded by python-dotenv
# inside core/llm_client_groq.py). On Streamlit Community Cloud, there is no
# .env file -- the key is instead set as a "secret" in the app's dashboard
# and exposed through st.secrets. Copying it into os.environ here means the
# existing llm_client_groq.py code works unchanged in both places.
#
# This MUST happen before importing llm_client_groq below, since that module
# creates its Groq client as soon as it's imported, not inside a function --
# the key needs to already be in the environment by then.
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass  # no secrets.toml locally -- that's fine, .env handles it instead

# Running locally is detected by the presence of a .env file, which only
# ever exists on your own machine (it's excluded from Git, so a deployed
# copy never has one). This same flag is reused further down to decide
# whether conversation persistence should be enabled -- see that section
# for why it matters.
IS_LOCAL = os.path.exists(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
)

# Pick ONE backend by uncommenting the import you want to use.
from core.llm_client_groq import ask_cyberprep
# from core.llm_client_ollama import ask_cyberprep
from core.prompt_template import SYSTEM_PROMPT
from core.chat_engine import handle_user_message

# --- Auto-build the knowledge base if it doesn't exist yet -------------
# Locally, you run knowledge_base/build_vector_db.py manually once. On a
# fresh deployment, there's no one to run that command -- so the app
# checks for the database on startup and builds it automatically the
# first time, the same way the manual script does.
from knowledge_base.db_location import CHROMA_DB_PATH as _CHROMA_DB_PATH

if not os.path.exists(_CHROMA_DB_PATH):
    with st.spinner("Setting up knowledge base for the first time..."):
        from knowledge_base.build_vector_db import build as _build_vector_db
        _build_vector_db()

# --- Conversation persistence (LOCAL USE ONLY) --------------------------
# Streamlit's session_state does NOT survive a hard browser refresh (F5) --
# a refresh opens a new session from Streamlit's point of view, wiping
# session_state back to empty. To fix this, the conversation is also saved
# to a local file after every turn, and reloaded from that file on
# startup if session_state is empty.
#
# This is gated behind IS_LOCAL on purpose: on a public deployment, every
# visitor would share the SAME saved file, meaning strangers could see
# each other's conversations -- a real privacy issue, not just a quirk.
# When deployed, this is skipped entirely, and Streamlit's normal
# per-visitor session_state is used instead, which is the correct,
# private behavior for a public app (a refresh there just starts fresh,
# same as any other hosted chatbot).
SESSION_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "session_data", "current_conversation.json"
)


def _load_conversation():
    if IS_LOCAL and os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def _save_conversation(conversation):
    if not IS_LOCAL:
        return
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(conversation, f)
    except OSError:
        pass


# Themed status words shown while processing a multi-term request (one of
# these is picked at random each time a new term starts). A normal
# single-question request never triggers this -- it keeps the plain
# "Thinking..." label the whole time, since on_progress is never called
# in that path.
CYBER_VERBS = [
    "Decrypting", "Analysing traffic", "Enumerating", "Scanning ports",
    "Cross-referencing threat intel", "Parsing logs", "Hardening defenses",
    "Correlating indicators", "Mapping attack surface", "Compiling findings",
    "Triaging alerts", "Fingerprinting services", "Reviewing packet captures",
    "Consulting MITRE ATT&CK",
]

# Custom CSS. Streamlit's theme config (.streamlit/config.toml) handles
# native widgets like buttons and the spinner, but it has no concept of
# "chat bubbles aligned left/right" -- that layout doesn't exist as a
# built-in Streamlit feature, so we build it ourselves with raw HTML/CSS.
st.markdown(
    """
    <style>
    /* Body font -- Aptos (Microsoft's current default Office font). Not a
       web font, so no @import is possible -- this renders correctly if
       Aptos is installed locally (it ships with recent Microsoft 365 /
       Windows installs), and falls back gracefully to Segoe UI /
       generic sans-serif if not. */
    html, body, .stApp, input, textarea, button, [data-testid="stChatInput"] * {
        font-family: 'Aptos', 'Segoe UI', -apple-system, sans-serif !important;
    }

    /* The "CyberPrep" brand plaque -- a small embossed panel with the
       title engraved into it, matching the monochromatic theme. */
    .brand-plaque {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 20px;
        width: fit-content;
        background: linear-gradient(145deg, #131315, #09090a);
        border: 1px solid #222225;
        border-radius: 10px;
        box-shadow:
            inset 0 1px 2px rgba(255, 255, 255, 0.04),
            inset 0 -1px 3px rgba(0, 0, 0, 0.7);
    }
    .brand-icon {
        font-size: 1.5rem;
        color: #4a4a4e;
    }
    .brand-title {
        /* Magneto -- a decorative Windows/Office font. Same local-font
           dependency as Aptos above; falls back to a generic cursive
           style if not installed. */
        font-family: 'Magneto', cursive;
        font-size: 2.1rem;
        letter-spacing: 1.5px;
        color: #3a3a3e;
        text-shadow:
            -1px -1px 1px rgba(0, 0, 0, 0.9),
            1px 1px 1px rgba(255, 255, 255, 0.08);
    }

    /* Mobile responsiveness -- everything above was sized and spaced by
       eye on a desktop browser, with no consideration for how it scales
       down to a phone-width screen. On narrow viewports, Streamlit stacks
       the header's two columns vertically, but the fixed desktop sizing
       (large padding, large font) still looked disproportionate next to
       such a narrow surrounding layout -- this scales those same
       elements down for anything phone-width or narrower. */
    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .brand-plaque {
            padding: 8px 14px;
            gap: 8px;
        }
        .brand-icon {
            font-size: 1.1rem;
        }
        .brand-title {
            font-size: 1.5rem;
            letter-spacing: 1px;
        }
        .user-bubble {
            max-width: 85%;
        }
        .assistant-bubble {
            max-width: 100%;
        }
    }

    /* Keep the header row (logo + Clear Chat button) pinned to the top
       of the screen while scrolling through chat history. Targets
       Streamlit's column-row wrapper directly -- this is the only
       st.columns() used on the page, so it's safe to target broadly. */
    div[data-testid="stHorizontalBlock"] {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: #0d0d0f;
        padding-top: 10px;
        padding-bottom: 14px;
    }

    /* Clear Chat button -- same embossed plaque treatment and engraved
       text style as the logo, but deliberately NOT using the Magneto
       font -- it keeps whatever font is already active (Aptos). */
    div[data-testid="stButton"] button {
        background: linear-gradient(145deg, #131315, #09090a) !important;
        border: 1px solid #222225 !important;
        border-radius: 10px !important;
        box-shadow:
            inset 0 1px 2px rgba(255, 255, 255, 0.04),
            inset 0 -1px 3px rgba(0, 0, 0, 0.7) !important;
        color: #3a3a3e !important;
        text-shadow:
            -1px -1px 1px rgba(0, 0, 0, 0.9),
            1px 1px 1px rgba(255, 255, 255, 0.08) !important;
        font-weight: 600 !important;
    }
    div[data-testid="stButton"] button:hover {
        color: #6a6a6e !important;
        border-color: #2e2e32 !important;
    }

    /* Hide Streamlit's default menu, footer, and header bar for a
       cleaner, custom look -- we're replacing the header with our own. */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Force full-width usage instead of Streamlit's default centered,
       narrow column. */
    .block-container {
        max-width: 100% !important;
        padding-left: 3rem;
        padding-right: 3rem;
        padding-top: 1.5rem;
    }

    .stApp {
        background-color: #0d0d0f;
    }

    /* One row per message. flex-end pushes user bubbles to the right,
       flex-start keeps assistant text on the left. */
    .chat-row {
        display: flex;
        margin: 14px 0;
    }
    .user-row {
        justify-content: flex-end;
    }
    .assistant-row {
        justify-content: flex-start;
    }

    /* User messages: a solid gunmetal-grey bubble, right-aligned. */
    .user-bubble {
        background-color: #2a2a2e;
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 16px;
        border-bottom-right-radius: 4px;
        max-width: 65%;
        line-height: 1.5;
    }

    /* Assistant messages: plain flowing text, no bubble -- matches the
       look of most modern AI chat interfaces, where only the user's
       side gets a boxed bubble. */
    .assistant-bubble {
        background-color: transparent;
        color: #e5e5e5;
        padding: 4px 0;
        max-width: 85%;
        line-height: 1.6;
    }

    /* Keyword highlighting -- grey-toned to stay monochromatic, rather
       than the amber used in the earlier version. */
    strong {
        background-color: rgba(255, 255, 255, 0.14);
        color: #ffffff;
        padding: 1px 5px;
        border-radius: 4px;
        font-weight: 700;
    }

    /* Basic table styling, since some answers include comparison tables. */
    .assistant-bubble table {
        border-collapse: collapse;
        margin: 10px 0;
    }
    .assistant-bubble th, .assistant-bubble td {
        border: 1px solid #3a3a3e;
        padding: 6px 12px;
        color: #e5e5e5;
    }

    /* The "Thinking..." / progress status box -- styled to match the
       monochromatic theme instead of Streamlit's default appearance.
       Targets both possible internal testids defensively, since status
       is built on top of Streamlit's expander component internally. */
    div[data-testid="stStatusWidget"], div[data-testid="stExpander"] {
        background-color: #131315 !important;
        border: 1px solid #222225 !important;
        border-radius: 10px !important;
    }

    .empty-state {
        color: #6e6e72;
        text-align: center;
        margin-top: 15vh;
        font-size: 1.1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom header row -- title on the left, Clear Chat button on the right.
# No sidebar at all, per the redesign.
header_col1, header_col2 = st.columns([6, 1])
with header_col1:
    st.markdown(
        '<div class="brand-plaque">'
        '<span class="brand-icon">🛡︎</span>'
        '<span class="brand-title">CyberPrep</span>'
        "</div>",
        unsafe_allow_html=True,
    )
with header_col2:
    if st.button("Clear Session", use_container_width=True):
        st.session_state.conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
        _save_conversation(st.session_state.conversation)
        st.rerun()

# session_state keeps the conversation alive across Streamlit's re-runs
# within the SAME session. On first load (or after a refresh, which starts
# a new session), fall back to whatever was last saved to disk.
if "conversation" not in st.session_state:
    st.session_state.conversation = _load_conversation()

# Render the full conversation as one block of HTML, with each message
# converted from Markdown to HTML first (so bold keywords and tables
# still render correctly inside the custom bubbles).
visible_messages = [m for m in st.session_state.conversation if m["role"] != "system"]

if not visible_messages:
    st.markdown(
        '<div class="empty-state">Ask. Learn. Secure.</div>',
        unsafe_allow_html=True,
    )
else:
    chat_html = ""
    for message in visible_messages:
        html_content = md_lib.markdown(message["content"], extensions=["tables"])
        if message["role"] == "user":
            chat_html += (
                f'<div class="chat-row user-row">'
                f'<div class="user-bubble">{html_content}</div></div>'
            )
        else:
            chat_html += (
                f'<div class="chat-row assistant-row">'
                f'<div class="assistant-bubble">{html_content}</div></div>'
            )
    st.markdown(chat_html, unsafe_allow_html=True)

# Chat input box fixed at the bottom of the page.
question = st.chat_input("There’s always another vulnerability to discover...")

if question:
    with st.status("Decrypting...", expanded=False) as status_box:

        def _on_progress(current, total, term):
            verb = random.choice(CYBER_VERBS)
            status_box.update(label=f"{verb}...")

        try:
            handle_user_message(
                st.session_state.conversation,
                question,
                ask_cyberprep,
                on_progress=_on_progress,
            )
        except Exception as e:
            # get_response already rolled back the failed question from
            # history -- re-add it here along with a visible error message,
            # so the user can see what they asked rather than having it
            # silently vanish.
            st.session_state.conversation.append({"role": "user", "content": question})
            st.session_state.conversation.append(
                {
                    "role": "assistant",
                    "content": f"Error: {e}\n\nCheck that your API key is set correctly in `.env`.",
                }
            )
    _save_conversation(st.session_state.conversation)
    st.rerun()
