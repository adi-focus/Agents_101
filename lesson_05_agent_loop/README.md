# Lesson 5: The agent loop

**Goal:** turn lesson 4's single round trip into a loop that keeps calling tools until the
mission is complete. That loop is an agent.

---

## 1. Lesson 4's cliff

In lesson 4, exercise 6, the model needed *two* tools, one after the other: get the weather,
then convert it. Your code did one round trip and stopped, so the second request was never
answered.

The fix is small: **keep going while the model keeps asking for tools.**

## 2. The whole idea in ten lines

```python
messages = [{"role": "user", "content": mission}]

while True:
    response = client.messages.create(model=MODEL, max_tokens=16000,
                                      tools=TOOLS, messages=messages)
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":
        break                                   # it's done (or stuck): stop looping

    results = [run_tool(b) for b in response.content if b.type == "tool_use"]
    messages.append({"role": "user", "content": results})
```

That's an agent. Everything else is making it **safe**, **visible** and **useful**.

```
          ┌──────────────────────────────────────────┐
          ▼                                          │
   ┌─────────────┐  tool_use   ┌────────────────┐    │
   │ call model  │────────────►│ run the tools  │────┘  append results to messages
   └─────────────┘             └────────────────┘
          │ end_turn
          ▼
        done
```

## 3. What changed from lesson 3 to lesson 5

| | Chatbot (lesson 3) | Agent (lesson 5) |
|---|---|---|
| Who writes the next `user` message? | A human | Your code (tool results) |
| When does a turn end? | After one reply | When the model stops asking for tools |
| Who decides the steps? | The human, one message at a time | The model |

Compare with lesson 1, exercise 5: there, *you* wrote the plan (geocode → fetch → compare). Here,
you give the model a goal and some tools, and it works out the plan.

## 4. Making it safe

A loop that lets a model choose actions needs guard rails:

- **A step limit.** If the model gets confused, `while True` runs (and bills you) forever. Use
  `for step in range(max_steps)` instead.
- **Handle every `stop_reason`.** `end_turn` means done. `max_tokens` means the reply was cut
  off. `refusal` means it declined. Don't treat these as "done", and don't crash: report them.
- **Errors go back to the model.** A failing tool returns `is_error: True` (lesson 4). The model
  can often fix its own mistake, such as a misspelled city.
- **Limit what tools can touch.** `write_file` here can only write inside `agent_workspace/`.
  A tool is code you're letting a model trigger, so give it only the permissions it needs.
- **A human approves risky actions.** Before anything irreversible, ask a person first.

## 5. Making it visible

Print a **trace** of every step: which tool, with what input, and what came back. When an agent
does something odd, the trace is how you find out why. You'll add this in exercise 2.

---

## The starter code

[`agent.py`](agent.py) has three tools ready: `get_coordinates`, `get_forecast` (your lesson 1
code, extended to tomorrow's forecast) and `write_file`. The loop is yours to write.

The default mission:

> Which of Lisbon, Cairo and Tokyo will have the highest maximum temperature tomorrow? Write a
> short picnic recommendation to `picnic.md`, including the numbers you used.

Solving it takes about seven tool calls: three geocodes, three forecasts and one write. You
won't tell it that. It works it out.

## Assignments

1. **Write the loop.** Fill in the `TODO`s in `run_agent()` in [`agent.py`](agent.py). Run
   `python3 agent.py`, then open `agent_workspace/picnic.md`.
2. **Add a trace.** For each step, print the step number, every text block, and every tool call
   with its input and the first 200 characters of its result. Run again and read the trace. Did
   it make several tool calls in one step (parallel calls)?
3. **Predict → Run → Explain: the step limit.** Predict what happens with `max_steps=2`, then run
   it. Does your code report it clearly, or fail silently?
4. **New mission, same code.** Without changing any code, give it a different mission (pass it
   as a command-line argument: `python3 agent.py "your mission"`). For example: *"Is it going to
   rain in London in the next 3 days? Save a packing list to london.md."* Why does this work
   without new code?
5. **Your own tool.** Add `read_file(filename)` (limited to `agent_workspace/`, like
   `write_file`). Then try: *"Read picnic.md and rewrite it as a haiku in haiku.md."*
6. **Human approval.** Before `write_file` runs, show the filename and the first lines of content
   and ask `Allow? [y/N]`. On "no", send back a `tool_result` saying the user declined. How does
   the model react?
7. **Reflection (in `notes.md`).** In three sentences: what is an agent? What does the model
   do, and what does your code do?

**Done when:** `python3 agent.py` completes the default mission on its own, prints a readable
trace, stops cleanly at the step limit, and asks you before writing any file.

---

## Where to go next

You've built the core loop that agent frameworks run. Possible next lessons:

- **Streaming:** print the model's words as they're generated instead of waiting.
- **The SDK's Tool Runner** (`client.beta.messages.tool_runner`): the SDK runs this loop for you,
  and builds tool schemas from Python type hints. You'll know what it's doing, because you wrote
  it yourself.
- **Context management:** every tool result grows `messages` (lesson 3). Long missions need
  trimming, summarising or *compaction*.
- **Hosted agents:** Claude Managed Agents runs the loop and a sandbox (bash, files, code) on
  Anthropic's side, so you don't host it.
- **Evaluation:** how do you know if a change to a prompt or tool made the agent better?
