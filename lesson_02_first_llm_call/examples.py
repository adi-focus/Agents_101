"""Lesson 2 examples: the same call with the official SDK.

Run:  python3 examples.py
"""
import anthropic

MODEL = "claude-opus-5-5"

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from the environment

# --- Example 1: the basic call ----------------------------------------------
response = client.messages.create(
    model=MODEL,
    max_tokens=16000,
    messages=[{"role": "user", "content": "Explain what an API is in one sentence."}],
)

print("=== Example 1: the whole response object ===")
print(response.model_dump_json(indent=2))   # same shape as the raw JSON in raw_http.py

print("\n=== Example 1: just the useful bits ===")
for block in response.content:              # content is a LIST of blocks
    print(f"block type: {block.type}")
    if block.type == "text":
        print("  text:", block.text)
print("stop_reason:", response.stop_reason)
print("usage:", response.usage.input_tokens, "in /", response.usage.output_tokens, "out")

# --- Example 2: a system prompt ---------------------------------------------
response = client.messages.create(
    model=MODEL,
    max_tokens=16000,
    system="You are a grumpy librarian. Answer correctly, but complain about it.",
    messages=[{"role": "user", "content": "Explain what an API is in one sentence."}],
)

print("\n=== Example 2: with a system prompt ===")
for block in response.content:
    if block.type == "text":
        print(block.text)
