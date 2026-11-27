"""Lesson 3 solution. Try the assignment before reading this."""
import anthropic

MODEL = "claude-opus-5-5"
SYSTEM = "You are a friendly, concise assistant. Keep replies to 1-3 sentences."

client = anthropic.Anthropic()


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    return "".join(b.text for b in content if getattr(b, "type", None) == "text")


def chat():
    messages = []
    total_in = 0
    total_out = 0

    while True:
        user_input = input("\nYou: ").strip()
        if user_input == "quit":
            break
        if not user_input:
            continue

        # Exercise 4 + 5: commands
        if user_input == "/reset":
            messages = []
            print("(history cleared)")
            continue
        if user_input == "/history":
            for m in messages:
                print(f"  {m['role']:>9}: {text_of(m['content'])[:60]!r}")
            continue
        if user_input == "/tokens":
            print(f"  session total: in={total_in} out={total_out}")
            continue
        if user_input == "/forget":
            # Assumes no API call failed partway through a turn, so the list
            # always ends with a complete user/assistant pair.
            messages = messages[:-2]
            print("(forgot the last exchange)")
            continue

        # Exercise 2: the chat turn
        messages.append({"role": "user", "content": user_input})
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            messages=messages,
        )
        print("Bot:", text_of(response.content))
        messages.append({"role": "assistant", "content": response.content})

        # Exercise 3: token growth
        total_in += response.usage.input_tokens
        total_out += response.usage.output_tokens
        print(f"  [in={response.usage.input_tokens} out={response.usage.output_tokens}]")


# Exercise 3 answer: input tokens grow because every request resends the whole
#   history (system prompt + every earlier user and assistant message).
# Exercise 5 answer: after /forget, the fact is gone from `messages`, so the
#   model has never "heard" it. Its memory is exactly the list you send.

if __name__ == "__main__":
    chat()
