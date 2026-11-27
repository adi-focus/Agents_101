"""Lesson 2 solution. Try the assignment before reading this."""
import anthropic

MODEL = "claude-opus-5-5"
INPUT_PRICE_PER_MTOK = 4.00
OUTPUT_PRICE_PER_MTOK = 20.00

client = anthropic.Anthropic()

# Exercise 3 answer: stop_reason is "max_tokens". There may be no text block at
# all, because the model spent its 10 tokens thinking before it started writing.
# Your code knows the answer was cut off by checking stop_reason.


# Exercise 4
QUESTION = "Why is the sky blue?"
SYSTEM_PROMPTS = [
    "You are a pirate.",
    "You are a teacher explaining things to a five-year-old.",
    "You are a cautious lawyer.",
    "You are a haiku poet. Answer only in haiku.",
]

def exercise_4():
    for system in SYSTEM_PROMPTS:
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": QUESTION}],
        )
        text = "".join(b.text for b in response.content if b.type == "text")
        print(f"--- {system}\n{text}\n")


# Exercises 5 and 6b
def ask(question: str, system: str | None = None) -> str:
    kwargs = {
        "model": MODEL,
        "max_tokens": 16000,
        "messages": [{"role": "user", "content": question}],
    }
    if system is not None:
        kwargs["system"] = system

    try:
        response = client.messages.create(**kwargs)
    except anthropic.AuthenticationError:
        print("Your API key is invalid. Check ANTHROPIC_API_KEY.")
        return ""
    except anthropic.RateLimitError:
        print("Slow down: you've hit the rate limit. Wait a moment and try again.")
        return ""
    except anthropic.APIConnectionError:
        print("Can't reach the API, check your internet connection.")
        return ""

    usage = response.usage
    cost = (usage.input_tokens / 1e6 * INPUT_PRICE_PER_MTOK
            + usage.output_tokens / 1e6 * OUTPUT_PRICE_PER_MTOK)
    print(f"[tokens in={usage.input_tokens} out={usage.output_tokens} · ~${cost:.4f}]")

    if response.stop_reason == "max_tokens":
        print("Warning: the answer was cut off (hit max_tokens).")

    return "".join(b.text for b in response.content if b.type == "text")


# Exercise 6a answer: 401, raised as anthropic.AuthenticationError.


if __name__ == "__main__":
    exercise_4()
    print(ask("What is an API? One sentence."))
    print(ask("What is an API?", system="Answer in exactly five words."))
