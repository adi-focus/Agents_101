"""Lesson 3 assignment: build a chatbot with memory.

Run:  python3 assignment.py
Type messages and press Enter. Type `quit` to exit.
"""
import anthropic

MODEL = "claude-opus-5-5"
SYSTEM = "You are a friendly, concise assistant. Keep replies to 1-3 sentences."

client = anthropic.Anthropic()


def text_of(content) -> str:
    """Join the text blocks in a list of content blocks.

    Message content can be a plain string (what you type) or a list of blocks
    (what the model returns), so handle both.
    """
    if isinstance(content, str):
        return content
    return "".join(b.text for b in content if getattr(b, "type", None) == "text")


def chat():
    messages = []          # the conversation's entire memory lives in this list
    total_in = 0
    total_out = 0

    while True:
        user_input = input("\nYou: ").strip()
        if user_input == "quit":
            break
        if not user_input:
            continue

        # -------------------------------------------------------------------
        # Exercise 4: commands. Handle these BEFORE calling the API, then
        # `continue` so that commands aren't sent to the model.
        #   /reset    -> clear messages
        #   /history  -> print each message: role + first 60 chars of its text
        #   /tokens   -> print total_in and total_out
        # Exercise 5 (stretch):
        #   /forget   -> remove the last user+assistant pair (the last 2 items)
        # -------------------------------------------------------------------
        # TODO

        # -------------------------------------------------------------------
        # Exercise 2: the chat turn
        # -------------------------------------------------------------------
        # TODO 1: append the user's message to `messages`
        # TODO 2: call client.messages.create(model=..., max_tokens=16000,
        #         system=SYSTEM, messages=messages)
        # TODO 3: print the reply text:  print("Bot:", text_of(response.content))
        # TODO 4: append the reply to `messages`, using response.content as-is
        raise NotImplementedError("Exercise 2")

        # -------------------------------------------------------------------
        # Exercise 3: watch the tokens grow
        # -------------------------------------------------------------------
        # TODO: print response.usage.input_tokens and response.usage.output_tokens,
        #       and add them to total_in / total_out


if __name__ == "__main__":
    chat()
