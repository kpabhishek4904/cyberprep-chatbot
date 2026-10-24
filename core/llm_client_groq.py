"""
LLM backend using Groq's free-tier cloud API.

Setup:
1. Create a free account at https://console.groq.com
2. Generate an API key from the dashboard
3. Create a .env file in the project root (copy .env.example) and paste your key in
4. pip install groq python-dotenv
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Groq hosts several open models for free -- this is a strong, fast default.
# Check https://console.groq.com/docs/models for the current list if this
# model name becomes unavailable in the future (Groq updates their lineup
# periodically, so don't be surprised if this needs changing again later).
MODEL = "openai/gpt-oss-20b"


def ask_cyberprep(messages: list) -> str:
    """
    Send the full conversation history (including the system prompt as the
    first message) to the LLM and return the latest answer. Passing the full
    history -- not just the newest question -- is what gives the chatbot
    memory of earlier turns, so follow-up questions actually work.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,  # lower temperature = more consistent, less "creative" formatting
        max_tokens=2048,  # gpt-oss-20b is a reasoning model -- its hidden "thinking"
                          # tokens are drawn from this same budget. Lowered back down
                          # from 6000 now that Option A (per-term looping in
                          # chat_engine.py) handles multi-term requests by making many
                          # small focused calls instead of one giant response -- no
                          # single call needs a huge budget anymore. Keeping this
                          # lower also leaves much more of Groq's free-tier
                          # tokens-per-minute budget (8000 TPM) available for actual
                          # conversation history, which matters now that conversations
                          # persist across sessions instead of resetting each time.
        reasoning_effort="medium",  # raised from "low" now that max_tokens has
                                     # plenty of headroom. Complex requests (e.g.
                                     # explaining many terms in one response with
                                     # consistent formatting throughout) benefit
                                     # from more actual "thinking" time to track
                                     # its own instructions across a long answer.
                                     # Trade-off: slightly slower responses.
    )
    return response.choices[0].message.content
