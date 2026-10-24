# Phase 5 Testing -- Glossary Expansion (26 -> 55 terms)

Validates that the newly added 29 terms work correctly, and that nothing
about the original 26 terms or the model's formatting behavior broke in
the process.

---

## Section 1 -- New Term Grounding Checks
Ask these directly and confirm the answer reflects your glossary's actual
wording (specific phrases, examples, or tool names from the JSON entry --
same technique used in Phase 3 to confirm Firewall/SIEM were genuinely
grounded, not just coincidentally good).

- What is SOC?
- What is the CIA triad?
- What is MITRE ATT&CK?
- What is XSS?
- What is kerberoasting?
- What is pass-the-hash?
- What is prompt injection?

---

## Section 2 -- Confusable Neighbor Pairs (the important one)
These terms are conceptually close to each other. The real risk after a
big expansion is retrieval pulling the WRONG neighbor, or the model
blending two related concepts together. Ask each one separately and
confirm the answer stays specifically on that term, not its neighbor.

- What is a vulnerability?
- What is an exploit?
- What is risk in cybersecurity?
  *(Check: these three should NOT read like copies of each other)*

- What is authentication?
- What is authorization?
  *(Check: authentication's answer should not describe permissions;
  authorization's answer should not describe identity verification)*

- What is red team?
- What is blue team?
- What is purple team?
  *(Check: each answer should be distinct, not a reworded version of
  the other two)*

---

## Section 3 -- Regression Check (original terms, pre-expansion)
Re-run a few of your original Phase 3 "gold standard" tests. These should
look exactly as good as they did before -- if something changed here,
that's a sign the expansion affected retrieval quality for old content.

- What is encryption?
- What is a firewall?
- What is SIEM?

---

## Section 4 -- Format-Type Regression Check
Confirms the LIST / HOW-TO / RECOMMENDATION classification rules (fixed
earlier in Phase 5) still work correctly now that there's much more
content in the knowledge base to retrieve from.

- List 10 terms related to Active Directory security
  *(Expect: a simple numbered list, NOT full 3W explanations)*
- How do I detect a pass-the-hash attack?
  *(Expect: direct practical answer, NOT a definition first)*
- Which tool is best for digital forensics?
  *(Expect: a direct recommendation, NOT the 3W structure)*

---

## Section 5 -- Off-Topic Control (should be unaffected)
- What's the capital of France?
  *(Expect: the proper redirect message, same as always)*

---

## Section 6 -- Multi-Term (Option A) Stress Test with New Content
Tests the per-term looping feature specifically against the newly added
Active Directory content.

1. Ask: "List 8 terms related to Active Directory attacks"
2. Then ask: "Explain each term"
3. Check: every term gets full, consistent 3W formatting and bolding --
   same bar as the earlier 20-term test that passed

---

## Section 7 -- AI Security Module (previously zero coverage)
- What is AI in cybersecurity?
- What is prompt injection?
  *(This whole category didn't exist before this expansion -- worth
  extra scrutiny since there's no prior baseline to compare against)*

---

## Notes / Observations
(Record anything that looks off here -- especially any neighbor-term
bleed from Section 2, since that's the highest-risk area after adding
this many related terms at once.)
