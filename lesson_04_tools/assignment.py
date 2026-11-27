"""Lesson 4 assignment: tools by hand.

Run:  python3 assignment.py
Set the EXERCISE number below to choose which exercise runs.
"""
import anthropic
import requests

MODEL = "claude-opus-5-5"
EXERCISE = 1          # <- change this as you go: 1, 2, 3, 4, 5, 6

client = anthropic.Anthropic()


# =============================================================================
# The tools: plain Python functions
# =============================================================================
def get_weather(city: str) -> str:
    print(f"    [running get_weather({city!r})]")
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1}, timeout=30,
    ).json()
    if not geo.get("results"):
        raise ValueError(f"City not found: {city}")
    place = geo["results"][0]
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": place["latitude"], "longitude": place["longitude"],
                "current": "temperature_2m,wind_speed_10m"},
        timeout=30,
    ).json()["current"]
    return (f"{place['name']}, {place.get('country', '')}: "
            f"{weather['temperature_2m']}°C, wind {weather['wind_speed_10m']} km/h")


def convert_c_to_f(celsius: float) -> str:
    print(f"    [running convert_c_to_f({celsius!r})]")
    return f"{celsius}°C = {celsius * 9 / 5 + 32:.1f}°F"


# =============================================================================
# The tool descriptions: what the model sees
# =============================================================================
WEATHER_TOOL = {
    "name": "get_weather",
    "description": "Get the current temperature (°C) and wind speed (km/h) for a city. "
                   "Use this whenever the user asks about current weather somewhere.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name, e.g. 'Tokyo'"}},
        "required": ["city"],
    },
}

# Exercise 4: write this schema yourself. Look at WEATHER_TOOL for the shape.
# The input is a number, so use {"type": "number"}.
CONVERT_TOOL = {
    # TODO: name, description, input_schema
}

# This maps tool names (what the model asks for) to functions (what we run).
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "convert_c_to_f": convert_c_to_f,
}


def print_blocks(response):
    print(f"  stop_reason = {response.stop_reason}")
    for block in response.content:
        if block.type == "text":
            print(f"  [text]     {block.text}")
        elif block.type == "tool_use":
            print(f"  [tool_use] id={block.id} name={block.name} input={block.input}")
        else:
            print(f"  [{block.type}]")


# =============================================================================
# Exercise 1: no tools  (Predict -> Run -> Explain)
# =============================================================================
def exercise_1():
    response = client.messages.create(
        model=MODEL, max_tokens=16000,
        messages=[{"role": "user", "content": "What's the temperature in Tokyo right now?"}],
    )
    print_blocks(response)


# =============================================================================
# Exercise 2: see the request
# =============================================================================
def exercise_2():
    # TODO: same question, but pass tools=[WEATHER_TOOL]. Print the blocks.
    #       Did "[running get_weather...]" appear? Why not?
    raise NotImplementedError("Exercise 2")


# =============================================================================
# Exercise 3: complete the round trip
# =============================================================================
def run_tool(tool_use) -> dict:
    """Run one tool_use block and return a tool_result block (a dict)."""
    # TODO:
    #   1. look up the function: TOOL_FUNCTIONS[tool_use.name]
    #   2. call it with the model's arguments: func(**tool_use.input)
    #   3. return {"type": "tool_result", "tool_use_id": tool_use.id, "content": <result string>}
    #
    # Exercise 5: wrap step 2 in try/except. On any Exception, return the
    #   error message as the content and add "is_error": True.
    raise NotImplementedError("run_tool")


def one_round_trip(question: str, tools: list[dict]):
    messages = [{"role": "user", "content": question}]

    # TODO 1: call the API with tools=tools; print_blocks(response)
    # TODO 2: if response.stop_reason != "tool_use": return (it answered directly)
    # TODO 3: append the assistant's response.content to messages
    # TODO 4: build a tool_result for EVERY tool_use block in response.content
    #         (use run_tool), and append them all in ONE user message
    # TODO 5: call the API again and print_blocks(response)
    raise NotImplementedError("Exercise 3")


# =============================================================================
if __name__ == "__main__":
    if EXERCISE == 1:
        exercise_1()
    elif EXERCISE == 2:
        exercise_2()
    elif EXERCISE == 3:
        one_round_trip("What's the weather in Tokyo right now?", [WEATHER_TOOL])
    elif EXERCISE == 4:
        one_round_trip("What's 31°C in Fahrenheit?", [WEATHER_TOOL, CONVERT_TOOL])
    elif EXERCISE == 5:
        one_round_trip("What's the weather in Atlantis right now?", [WEATHER_TOOL])
    elif EXERCISE == 6:
        # Predict first: how many tool calls does this need? Does your code handle that?
        one_round_trip("What's the temperature in Tokyo right now, in Fahrenheit?",
                       [WEATHER_TOOL, CONVERT_TOOL])
