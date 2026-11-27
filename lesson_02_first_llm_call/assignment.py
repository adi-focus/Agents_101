"""Lesson 2 assignment: your first LLM call.

Exercises 1-2 are in the README (run raw_http.py and examples.py, take notes).
This file covers exercises 3-6. Run `python3 assignment.py` after each one.
"""
import anthropic

MODEL = "claude-opus-5-5"

# Prices in dollars per million tokens for claude-opus-5-5.
# Check https://claude.com/pricing and update these if you change MODEL.
INPUT_PRICE_PER_MTOK = 4.00
OUTPUT_PRICE_PER_MTOK = 20.00

client = anthropic.Anthropic()


# =============================================================================
# Exercise 3: tiny max_tokens  (Predict -> Run -> Explain)
# =============================================================================
# In notes.md, predict BEFORE running:
#   - What will stop_reason be?
#   - Will there be a text block at all? (Remember: the model may think first,
#     and thinking uses tokens too.)
# Then set RUN_EXERCISE_3 = True.
RUN_EXERCISE_3 = False

def exercise_3():
    response = client.messages.create(
        model=MODEL,
        max_tokens=10,
        messages=[{"role": "user", "content": "Write a 300-word story about a robot chef."}],
    )
    print("stop_reason:", response.stop_reason)
    print("block types:", [b.type for b in response.content])
    for block in response.content:
        if block.type == "text":
            print("text:", repr(block.text))
    # Explain: if this happened inside a program, how would your code know the
    # answer was cut off?


# =============================================================================
# Exercise 4: system prompts
# =============================================================================
# Ask QUESTION once for each system prompt below and print the answers.
# Add a fourth system prompt of your own.

QUESTION = "Why is the sky blue?"
SYSTEM_PROMPTS = [
    "You are a pirate.",
    "You are a teacher explaining things to a five-year-old.",
    "You are a cautious lawyer.",
    # TODO: add your own
]

def exercise_4():
    for system in SYSTEM_PROMPTS:
        # TODO: call client.messages.create with system=system, print the text
        raise NotImplementedError("Exercise 4")


# =============================================================================
# Exercise 5: ask(question, system=None) -> str
# =============================================================================
# Requirements:
#   - Calls the API (pass `system` only if it isn't None)
#   - Returns ONLY the text: join every block where block.type == "text"
#   - Prints:  [tokens in=<n> out=<n> · ~$<cost>]
#     cost = in_tokens/1e6 * INPUT_PRICE + out_tokens/1e6 * OUTPUT_PRICE
#   - If stop_reason is "max_tokens", print a warning that the answer was cut off

def ask(question: str, system: str | None = None) -> str:
    # Hint: build the arguments in a dict, then call client.messages.create(**kwargs).
    # That lets you add "system" only when you have one.
    raise NotImplementedError("Exercise 5")


# =============================================================================
# Exercise 6: errors
# =============================================================================
# Part a) Predict: what HTTP status code does a fake key get? (Lesson 1, section 3.)
#         Set RUN_EXERCISE_6 = True and run it.
# Part b) Go back to ask() and wrap the API call in try/except so that:
#           anthropic.AuthenticationError -> print "Your API key is invalid..." and return ""
#           anthropic.RateLimitError      -> print "Slow down..." and return ""
#           anthropic.APIConnectionError  -> print "Can't reach the API, check your internet" and return ""
RUN_EXERCISE_6 = False

def exercise_6():
    bad_client = anthropic.Anthropic(api_key="sk-ant-this-is-not-a-real-key")
    try:
        bad_client.messages.create(
            model=MODEL, max_tokens=100,
            messages=[{"role": "user", "content": "hi"}],
        )
    except anthropic.APIStatusError as e:
        print("Status code:", e.status_code)
        print("Exception type:", type(e).__name__)
        print("Message:", e.message)


# =============================================================================
if __name__ == "__main__":
    if RUN_EXERCISE_3:
        exercise_3()
    try:
        exercise_4()
    except NotImplementedError as e:
        print("Not done yet:", e)
    try:
        print(ask("What is an API? One sentence."))
    except NotImplementedError as e:
        print("Not done yet:", e)
    if RUN_EXERCISE_6:
        exercise_6()
