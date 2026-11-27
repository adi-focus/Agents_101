# Lesson 4: Tools (the model asks, your code acts)

**Goal:** give the model a tool, watch it ask to use it, run the tool yourself, and send the
result back. This is one round trip, done by hand.

---

## 1. The model can only write text

Ask Claude "What's the temperature in Tokyo right now?" and it can't know. It has no internet,
no clock and no way to run code. All it can do is produce text.

But you can. In lesson 1 you wrote a function that fetches the weather. What if the model could
*ask you* to run it?

That is all **tool use** is:

```
 You                                   Claude
  │  "What's the weather in Tokyo?"     │
  │  + a menu of tools you can run  ───►│
  │                                     │  "I'd like you to run get_weather
  │◄─────────────────────────────────── │   with {"city": "Tokyo"}"   (stop_reason: tool_use)
  │                                     │
  │  YOU run get_weather("Tokyo")       │
  │  → "12.3°C, wind 9 km/h"            │
  │                                     │
  │  "Here's the result: 12.3°C…"  ────►│
  │                                     │
  │◄─────────────────────────────────── │  "It's 12.3°C in Tokyo right now."  (stop_reason: end_turn)
```

**The model never runs anything.** It only asks. Your code decides whether to run the tool,
runs it, and reports back. Every agent framework is built on this point.

## 2. Describing a tool

You describe each tool with a name, a description and an **input schema** (JSON Schema, a
standard way to say "this takes an object with a string field called `city`"):

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get the current temperature and wind speed for a city. "
                       "Use this whenever the user asks about current weather.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. 'Tokyo'"}
            },
            "required": ["city"],
        },
    }
]
```

The model reads the `description` to decide *when* to use the tool, and the schema to decide
*what to pass*. Write descriptions as if for a new colleague: say what the tool does, when to use
it and what it returns. A vague description gets a confused model.

## 3. The round trip in code

**Step 1: send the question with the tools.**
```python
messages = [{"role": "user", "content": "What's the weather in Tokyo?"}]
response = client.messages.create(model=MODEL, max_tokens=16000, tools=tools, messages=messages)
```

**Step 2: the model replies with a `tool_use` block** and `stop_reason == "tool_use"`:
```python
# response.content might be:
#   [ThinkingBlock(...),
#    TextBlock(text="I'll check the weather."),
#    ToolUseBlock(id="toolu_01A...", name="get_weather", input={"city": "Tokyo"})]
```

**Step 3: you run the tool and send back a `tool_result`:**
```python
tool_use = next(b for b in response.content if b.type == "tool_use")
result = get_weather(**tool_use.input)        # YOUR code runs here

messages.append({"role": "assistant", "content": response.content})   # its request, as-is
messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use.id,           # must match the request's id
        "content": result,                    # a string
    }],
})
```

**Step 4: call again.** The model reads the result and answers in plain text, with
`stop_reason == "end_turn"`.

A few details:
- The tool result goes in a **`user`** message. From the API's point of view, you (the code) are
  the one reporting back.
- `tool_use_id` links each result to its request, because the model can ask for **several tools
  in one reply**. When it does, run all of them and send all the results together in **one** user
  message.
- If the tool fails, still send a result, with `"is_error": True` and the error message in
  `content`. The model can often recover (for example, by fixing a misspelled city).

---

## Run the example

```bash
cd lesson_04_tools
python3 examples.py
```

## Assignments

Open [`assignment.py`](assignment.py).

1. **Predict → Run → Explain: no tools.** Ask "What's the temperature in Tokyo right now?"
   *without* tools. Predict the answer, then run it. Does it refuse, guess or hedge?
2. **See the request.** Send the same question *with* the tool. Print every block in
   `response.content` and the `stop_reason`. Check: did any weather code run? (Add a `print`
   inside `get_weather` to be sure.)
3. **Complete the round trip.** Run the tool, send back the `tool_result`, and print the final
   answer.
4. **Write a tool yourself.** Write the schema for `convert_c_to_f(celsius)`. Ask "What's 31°C
   in Fahrenheit?" and check that the model picks the right tool. Then change the description
   to something vague ("does stuff with numbers") and see if it still picks it.
5. **Errors.** Ask about the weather in "Atlantis". Your tool should return a result with
   `is_error: True`. What does the model say to the user?
6. **Predict → Run → Explain: the cliff.** Ask "What's the temperature in Tokyo, in
   Fahrenheit?". This needs *two* tools, one after the other. Predict what your one-round-trip
   code will do, then run it. What's missing? That is lesson 5.

**Done when:** "What's the weather in Tokyo?" prints a real temperature in a friendly sentence,
and you can explain why exercise 6 doesn't work.
