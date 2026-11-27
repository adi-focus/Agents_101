# Lesson 2: Your first LLM call

**Goal:** call Claude with plain HTTP, then with the official Python SDK, and understand every
field in the response: content blocks, `stop_reason` and token usage.

---

## 1. An LLM is just another API

In lesson 1 you sent a `GET` with query parameters. Calling Claude is a `POST` with a JSON
**body**. Everything else is the same idea.

```
POST https://api.anthropic.com/v1/messages

Headers:
  x-api-key: sk-ant-...             ← who you are (lesson 1, section 5)
  anthropic-version: 2026-10-21     ← which version of the API's rules to use
  content-type: application/json    ← "my body is JSON"

Body:
{
  "model": "claude-opus-5-5",
  "max_tokens": 16000,
  "messages": [
    {"role": "user", "content": "Explain an API in one sentence."}
  ]
}
```

| Body field | Meaning |
|---|---|
| `model` | Which model answers. |
| `max_tokens` | The most the model is allowed to write. It is a ceiling, not a target. |
| `messages` | The conversation so far. For now, a single `user` message. |
| `system` *(optional)* | Instructions that frame the whole conversation ("You are a pirate…"). |

## 2. The response

```json
{
  "id": "msg_01AbC...",
  "type": "message",
  "role": "assistant",
  "model": "claude-opus-5-5",
  "content": [
    {"type": "thinking", "thinking": "", "signature": "..."},
    {"type": "text", "text": "An API is a menu of requests one program can make of another."}
  ],
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 14, "output_tokens": 37}
}
```

Three things to notice:

**`content` is a list of blocks, not a string.** Each block has a `type`. Today you'll see
`thinking` (the model reasons before answering; by default you get an empty placeholder, not the
reasoning itself) and `text` (the answer). In lesson 4 you'll meet `tool_use`. So
`response["content"][0]["text"]` is a bug: the first block may not be text. Always loop over the
blocks and check their type.

**`stop_reason` says why the model stopped.**

| `stop_reason` | Meaning |
|---|---|
| `end_turn` | It finished what it wanted to say. |
| `max_tokens` | It hit your `max_tokens` limit, so the answer was cut off. |
| `tool_use` | It wants you to run a tool (lesson 4). |
| `refusal` | It declined the request. |

The agent loop in lesson 5 is built around this one field.

**`usage` counts tokens.** A token is a chunk of text, roughly ¾ of an English word. You pay
per token, at one price for input (what you send) and a higher price for output (what it
writes). Prices are listed at <https://claude.com/pricing>.

## 3. The SDK: the same request, with less typing

Writing headers and JSON by hand gets tedious. The official SDK (`pip install anthropic`) does
it for you:

```python
import anthropic

client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY from your environment

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    messages=[{"role": "user", "content": "Explain an API in one sentence."}],
)

for block in response.content:
    if block.type == "text":
        print(block.text)

print(response.stop_reason, response.usage.input_tokens, response.usage.output_tokens)
```

Under the hood this sends **exactly** the HTTP request from section 1. The SDK adds:
- objects instead of dicts (`response.content`, not `response["content"]`)
- automatic retries when the server is busy
- specific exceptions for errors: `anthropic.AuthenticationError` (401),
  `anthropic.RateLimitError` (429), `anthropic.APIConnectionError` (no network)

From lesson 3 on, you'll use the SDK.

---

## Run the examples

```bash
cd lesson_02_first_llm_call
python3 raw_http.py      # the request built by hand with `requests`
python3 examples.py      # the same thing with the SDK, plus a system prompt
```

## Assignments

Open [`assignment.py`](assignment.py).

1. **Label the response.** Run `raw_http.py`. In `notes.md`, label every top-level field in the
   printed JSON. Which fields would change if you asked the same question again?
2. **Spot the difference.** Run `examples.py`. Find the same fields on the SDK's response object.
3. **Predict → Run → Explain: tiny `max_tokens`.** Predict what happens with `max_tokens=10`:
   what will `stop_reason` be? Will there be any text at all? Run it. Explain what you see.
4. **System prompts.** Ask the same question with three different `system` prompts (a pirate, a
   five-year-old's teacher, a lawyer). Same model, same question: what changed and why?
5. **Write `ask(question, system=None) -> str`.** It should return only the text (joining all
   text blocks), and print the token usage and estimated cost of the call.
6. **Handle errors.** Call the API with a fake key and catch the error. Predict the status code
   first. Then make `ask()` print a friendly message instead of a stack trace.

**Done when:** `ask("What is an API?")` returns a clean string and prints a line like
`[tokens in=14 out=52 · ~$0.0011]`, and a bad key prints a friendly message instead of crashing.
