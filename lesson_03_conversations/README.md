# Lesson 3: Conversations (the model has no memory)

**Goal:** understand that every API call starts from nothing, and build a chatbot that remembers
by resending the whole conversation each turn.

---

## 1. The surprise

Run this in your head first. Two separate calls:

```python
ask("My name is Sam.")          # → "Nice to meet you, Sam!"
ask("What's my name?")          # → ???
```

The second call has no idea. **The API is stateless:** each request is handled on its own, as
if the model had never met you. Nothing is saved between calls.

So how does ChatGPT or claude.ai "remember"? **The app resends the entire conversation on every
turn.**

## 2. The `messages` list *is* the memory

```python
messages = [
    {"role": "user",      "content": "My name is Sam."},
    {"role": "assistant", "content": [...the blocks from the first response...]},
    {"role": "user",      "content": "What's my name?"},
]
```

The rules:
- Roles alternate: `user`, `assistant`, `user`, `assistant`, …
- The list starts with a `user` message.
- To continue, **append** the model's reply, then append the next user message, and send the
  whole list again.

```
Turn 1 sends:  [u1]                     → gets a1
Turn 2 sends:  [u1, a1, u2]             → gets a2
Turn 3 sends:  [u1, a1, u2, a2, u3]     → gets a3
```

When you append the model's reply, append **`response.content` as-is**: the full list of
blocks, including the `thinking` placeholder. Don't pull out just the text. This habit
matters in lesson 4, where the reply contains a tool request the API has to see again.

```python
messages.append({"role": "assistant", "content": response.content})
```

## 3. The cost of memory

Look at the diagram again. Every turn resends *everything before it*. So:

- **Input tokens grow every turn.** Turn 10 pays to send turns 1–9 again.
- **There is a limit,** the *context window*: the most tokens one request can hold (about a
  million for current Claude models). A long conversation eventually hits it.

Agents hit this constantly, because every tool result goes into `messages` too. Keep it in mind.

## 4. You control the memory

Because the history is just a Python list, *you* decide what the model remembers. You can clear
it (`/reset`), trim it, or start a new conversation with a different system prompt. The model
only knows what is in the list you send.

---

## Run the example

```bash
cd lesson_03_conversations
python3 examples.py
```

## Assignments

Open [`assignment.py`](assignment.py).

1. **Predict → Run → Explain: the forgetful model.** Predict what the second call returns, then
   run `examples.py` and compare.
2. **Build `chat()`.** A loop that reads your input, appends it to `messages`, calls the API,
   prints the reply, appends the reply, and repeats. `quit` exits.
3. **Watch the tokens grow.** After each reply, print `input_tokens` and `output_tokens`. Have
   a 6-turn conversation. In `notes.md`, write down the input tokens per turn. Why does the
   number grow even when your messages are short?
4. **Commands.** Add `/reset` (clear history), `/history` (print each message's role and the
   first 60 characters of its text) and `/tokens` (total tokens used this session).
5. **Stretch: rewrite history.** Add `/forget`, which removes the last user + assistant pair.
   Tell the bot a fact, `/forget` it, then ask about it. Explain what happened.

**Done when:** you can tell the bot your name, chat about something else for three turns, ask
"what's my name?" and get the right answer, then `/reset` and see it forget.
