"""Lesson 4 solution. Try the assignment before reading this."""
import anthropic
import requests

MODEL = "claude-opus-5-5"
EXERCISE = 3

client = anthropic.Anthropic()


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

# Exercise 4
CONVERT_TOOL = {
    "name": "convert_c_to_f",
    "description": "Convert a temperature from Celsius to Fahrenheit. "
                   "Use this whenever a temperature needs to be shown in °F.",
    "input_schema": {
        "type": "object",
        "properties": {"celsius": {"type": "number", "description": "Temperature in °C"}},
        "required": ["celsius"],
    },
}

TOOL_FUNCTIONS = {"get_weather": get_weather, "convert_c_to_f": convert_c_to_f}


def print_blocks(response):
    print(f"  stop_reason = {response.stop_reason}")
    for block in response.content:
        if block.type == "text":
            print(f"  [text]     {block.text}")
        elif block.type == "tool_use":
            print(f"  [tool_use] id={block.id} name={block.name} input={block.input}")
        else:
            print(f"  [{block.type}]")


# Exercise 2 (answer): with tools=[WEATHER_TOOL] you get stop_reason="tool_use"
# and a tool_use block, but "[running get_weather...]" never prints. The model
# only ASKED; nothing runs until your code runs it.
def exercise_2():
    response = client.messages.create(
        model=MODEL, max_tokens=16000, tools=[WEATHER_TOOL],
        messages=[{"role": "user", "content": "What's the temperature in Tokyo right now?"}],
    )
    print_blocks(response)


# Exercises 3 + 5
def run_tool(tool_use) -> dict:
    func = TOOL_FUNCTIONS[tool_use.name]
    try:
        output = func(**tool_use.input)
        return {"type": "tool_result", "tool_use_id": tool_use.id, "content": output}
    except Exception as e:
        return {"type": "tool_result", "tool_use_id": tool_use.id,
                "content": f"Error: {e}", "is_error": True}


def one_round_trip(question: str, tools: list[dict]):
    messages = [{"role": "user", "content": question}]

    response = client.messages.create(model=MODEL, max_tokens=16000, tools=tools, messages=messages)
    print_blocks(response)
    if response.stop_reason != "tool_use":
        return

    messages.append({"role": "assistant", "content": response.content})
    results = [run_tool(b) for b in response.content if b.type == "tool_use"]
    messages.append({"role": "user", "content": results})

    response = client.messages.create(model=MODEL, max_tokens=16000, tools=tools, messages=messages)
    print_blocks(response)


# Exercise 6 answer: the model usually calls get_weather, reads "12.3°C", then
# asks for convert_c_to_f. That second request has stop_reason="tool_use" again,
# but our code has already stopped, so the question never gets a final answer.
# (Sometimes the model does the arithmetic itself and skips the second tool. Run
# it a few times and see. You can't always predict which steps a model will take.)
# The fix is a loop: keep going while stop_reason == "tool_use". That is lesson 5.

if __name__ == "__main__":
    if EXERCISE == 2:
        exercise_2()
    elif EXERCISE == 3:
        one_round_trip("What's the weather in Tokyo right now?", [WEATHER_TOOL])
    elif EXERCISE == 4:
        one_round_trip("What's 31°C in Fahrenheit?", [WEATHER_TOOL, CONVERT_TOOL])
    elif EXERCISE == 5:
        one_round_trip("What's the weather in Atlantis right now?", [WEATHER_TOOL])
    elif EXERCISE == 6:
        one_round_trip("What's the temperature in Tokyo right now, in Fahrenheit?",
                       [WEATHER_TOOL, CONVERT_TOOL])
