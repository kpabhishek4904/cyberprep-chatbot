"""
CyberPrep -- Command-line interface

The terminal-based version of the chatbot. Useful for quick testing
without launching the full web UI. See streamlit_app.py for the web
version (Phase 4).
"""

# Pick ONE backend by uncommenting the import you want to use.
# Start with Groq unless you've specifically set up Ollama.
from core.llm_client_groq import ask_cyberprep
# from core.llm_client_ollama import ask_cyberprep
from core.prompt_template import SYSTEM_PROMPT
from core.chat_engine import handle_user_message


def main():
    print("=" * 60)
    print("  CyberPrep -- Cybersecurity Interview Prep Chatbot")
    print("  Command-line version")
    print("  Type 'exit' to quit, or 'reset' to start a fresh conversation")
    print("=" * 60)

    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        question = input("\nAsk about a cybersecurity term: ").strip()

        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        if question.lower() in ("reset", "new"):
            conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("Conversation history cleared. Starting fresh.")
            continue
        if not question:
            continue

        print("\nThinking...\n")
        try:
            answer = handle_user_message(conversation, question, ask_cyberprep)
            print(answer)
        except Exception as e:
            print(f"Error: {e}")
            print("Check that your API key is set correctly in .env")


if __name__ == "__main__":
    main()
