# Phase 3 Testing -- Validating RAG Actually Works

These tests check whether retrieval is genuinely improving answers, not
just running silently in the background without doing anything useful.

## Test 1 -- Direct term lookups (should be grounded)
Ask about terms that ARE in your glossary.json. Compare the answer's
wording against `testing/benchmark_answers.md` -- it should now line up
even more closely than in Phase 1, since the model is reading your
verified content directly.

- What is encryption?
- What is a firewall?
- What is SIEM?

## Test 2 -- A term NOT in your glossary (should still work gracefully)
Your knowledge base only has 12 terms. Ask about something outside it and
confirm the chatbot still answers sensibly, falling back to its own
general knowledge -- this proves the "no relevant match found" path works.

- What is SQL injection?
- What is a buffer overflow?

## Test 3 -- Revisit the earlier retrieval weak point
In Phase 2 testing, an ambiguous phishing-related query incorrectly
ranked Multi-Factor Authentication above Phishing. Test whether this
actually causes a wrong final answer now that the LLM sees multiple
retrieved results together, not just the top one.

- What is phishing? (direct -- should be unambiguous)
- What's something that tricks people into giving away their password?
  (the ambiguous phrasing -- pay close attention to whether the final
  answer is still accurate despite the earlier ranking issue)

## Test 4 -- Conversation memory still works
Confirm Phase 1's conversation memory fix didn't break with RAG added.

- Ask: What is directory enumeration?
- Then ask: Among the tools you mentioned, which is more beginner-friendly?

## Test 5 -- Off-topic still correctly declined
- What's the capital of France?

## Notes / Observations
(Record what you find here -- especially anything from Test 3, since
that's the one genuine open question carried over from Phase 2.)
