# Phase 1 Testing -- Term List

Run `app.py` and test it against these terms. For each one, check:

1. Did it follow the exact 3W format (What / Why / Where), with nothing extra?
2. Is the language genuinely simple -- could a complete beginner follow it?
3. Are the bolded keywords actually the ones an interviewer would expect?
4. Is it under ~150 words?

If an answer fails any of these, that's useful signal -- note what went wrong,
then adjust the wording in `core/prompt_template.py` and re-test.

## Core networking / fundamentals
- Firewall
- VPN
- DNS
- Port scanning

## Core security concepts
- Phishing
- Encryption
- Multi-factor authentication
- Zero-day vulnerability

## SOC / Blue Team relevant (since this is your target role)
- SIEM
- Incident response
- Threat intelligence
- False positive

## A deliberately tricky one
- Zero trust
  (This term is often explained badly/vaguely even by real candidates --
  good test of whether your prompt forces real precision)

## Off-topic test (should politely redirect, not answer)
- "What's the capital of France?"
- "Write me a poem about the ocean"

## Notes / Observations
(Keep your own running notes here as you test -- what worked, what didn't,
what you changed in the prompt and why.)

- Refresh button on the website clears the whole conversation.
- List 15 defensive security terms. Did not list 15 terms, instead went with the 3W structure and explained 15 terms, lacked necessary keywords. Did not number them properly.
- In that same session, asked what is brute forcing, answered correctly, then asked which tool is best for brute forcing, it did not answer. Not the usual reply like ' I'm focused on cybersecurity topics... ', it said ' I'm sorry, can't help with that. '. Started a new session and did the same thing, it answered much better than previous time and also did not reject to answer.
- Sometimes when I ask out of structure questions like which tool is best for directory enumeration, it still answers in 3W format instead of giving straightforward answers.
- Questions like how to perform packet analysis still uses 3W format to explain what is packet analysis. Had to ask the same question again to get the steps to perform packet analysis. Same goes for questions like which tool is best for something, answers it in 3W format but mentions which tool it suggests.
