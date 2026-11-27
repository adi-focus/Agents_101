"""Lesson 3 examples: the model is stateless, so history has to be resent.

Run:  python3 examples.py
"""
import anthropic

MODEL = "claude-opus-5-5"
client = anthropic.Anthropic()


def text_of(response) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


# --- Example 1: two separate calls, no shared history ------------------------
print("=== Example 1: two separate calls ===")
r1 = client.messages.create(
    model=MODEL, max_tokens=16000,
    messages=[{"role": "user", "content": "My name is Sam. Just say hi."}],
)
print("Call 1:", text_of(r1))

r2 = client.messages.create(
    model=MODEL, max_tokens=16000,
    messages=[{"role": "user", "content": "What's my name?"}],
)
print("Call 2:", text_of(r2))


# --- Example 2: the same two questions, sending the history ------------------
print("\n=== Example 2: resending the history ===")
messages = [{"role": "user", "content": "My name is Sam. Just say hi."}]
r1 = client.messages.create(model=MODEL, max_tokens=16000, messages=messages)
print("Turn 1:", text_of(r1))

messages.append({"role": "assistant", "content": r1.content})   # the model's reply, as-is
messages.append({"role": "user", "content": "What's my name?"})

r2 = client.messages.create(model=MODEL, max_tokens=16000, messages=messages)
print("Turn 2:", text_of(r2))

print("\nInput tokens, turn 1:", r1.usage.input_tokens, " turn 2:", r2.usage.input_tokens)
print("(Turn 2 costs more input because it resends turn 1.)")
