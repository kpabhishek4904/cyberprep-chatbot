"""
LLM backend using Ollama -- runs a model locally on your own machine, completely
free, no API key, no internet required once set up.

Setup:
1. Install Ollama from https://ollama.com
2. Pull a model:  ollama pull llama3.2
3. pip install ollama
4. Make sure the Ollama app/service is running in the background

Note: needs a reasonably capable machine (8GB+ RAM recommended for this model size).
If responses are very slow, try a smaller model like `ollama pull phi3`.
"""

import ollama

MODEL = "llama3.2"


def ask_cyberprep(messages: list) -> str:
    """
    Send the full conversation history (including the system prompt as the
    first message) to the local LLM and return the latest answer. Passing
    the full history -- not just the newest question -- is what gives the
    chatbot memory of earlier turns, so follow-up questions actually work.
    """
    response = ollama.chat(
        model=MODEL,
        messages=messages,
    )
    return response["message"]["content"]
