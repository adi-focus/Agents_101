# Agents 101: from an API call to an agent loop

This course builds an AI agent from scratch. There are no frameworks, so you see every moving part.
By the end you will have written about 100 lines of Python that take a mission, decide which
tools to call, call them, read the results, and keep going until the mission is done.

```
Lesson 1  What is an API?            HTTP, requests, responses, JSON, status codes
Lesson 2  Your first LLM call        The Claude API is just another API
Lesson 3  Conversations              The model has no memory; you resend the history
Lesson 4  Tools                      The model asks; your code does the work
Lesson 5  The agent loop             Repeat lesson 4 until the mission is complete
```

Each lesson builds on the one before it. The weather API you call by hand in lesson 1 becomes the
tool the agent uses in lesson 5.

## How each lesson works

Every lesson folder contains:

| File | What it is |
|---|---|
| `README.md` | The concepts, with small examples. Read this first. |
| `examples.py` | Working code from the README. Run it and change it. |
| `assignment.py` | Your exercises, marked `TODO`. This is where you do the work. |
| `solution.py` | One possible answer. Look at it only after you have tried. |

Two exceptions: lesson 2 also has `raw_http.py`, and in lesson 5 the starter file is
`agent.py` (it is both the example and the assignment).

Many exercises use a **Predict → Run → Explain** format:

1. **Predict.** Write down what you think will happen *before* running the code.
2. **Run.** Run it.
3. **Explain.** If you were wrong, work out why. That is where most of the learning happens.

Keep a `notes.md` file and write your predictions in it. Being wrong in writing teaches you more
than being wrong in your head.

## Setup (do this once)

1. **Python 3.10 or newer.** Check with `python3 --version`.
2. **Install the two libraries:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Get a Claude API key** from <https://console.anthropic.com> (Settings → API Keys). Lessons 2–5
   need it. Lesson 1 does not.
4. **Put the key in your environment.** Do not paste it into code files:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."      # add this line to ~/.zshrc to keep it
   ```
5. **Check it works:**
   ```bash
   python3 -c "import anthropic; print(anthropic.Anthropic().models.retrieve('claude-opus-5-5').display_name)"
   ```

### About cost

Lessons 2–5 call a paid API. A whole lesson usually costs a few cents. Every file sets the model
in one line at the top:

```python
MODEL = "claude-opus-5-5"
```

Lesson 2 shows you how to read the token counts and work out what each call cost.
