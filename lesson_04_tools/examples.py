"""Lesson 4 examples: one tool, one round trip, step by step.

Run:  python3 examples.py
"""
import anthropic
import requests

MODEL = "claude-opus-5-5"
client = anthropic.Anthropic()


# --- The tool: an ordinary Python function (your lesson 1 code) --------------
def get_weather(city: str) -> str:
    print(f"    [your code is running get_weather({city!r})]")
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


# --- The tool's description: what the MODEL sees -----------------------------
tools = [
    {
        "name": "get_weather",
        "description": "Get the current temperature (°C) and wind speed (km/h) for a city. "
                       "Use this whenever the user asks about current weather somewhere.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. 'Tokyo'"}},
            "required": ["city"],
        },
    }
]


def show(response):
    print(f"  stop_reason = {response.stop_reason}")
    for block in response.content:
        if block.type == "text":
            print(f"  [text]     {block.text}")
        elif block.type == "tool_use":
            print(f"  [tool_use] id={block.id} name={block.name} input={block.input}")
        else:
            print(f"  [{block.type}]")


# Step 1: ask, offering the tool
print("STEP 1: send the question + the tool menu")
messages = [{"role": "user", "content": "What's the weather in Tokyo right now?"}]
response = client.messages.create(model=MODEL, max_tokens=16000, tools=tools, messages=messages)

# Step 2: the model asks for the tool. Nothing has run yet.
print("\nSTEP 2: the model replies with a REQUEST (no weather code has run)")
show(response)

# Step 3: run the tool ourselves and send the result back
print("\nSTEP 3: we run the tool and send back a tool_result")
tool_use = next(b for b in response.content if b.type == "tool_use")
result = get_weather(**tool_use.input)
print(f"    result = {result!r}")

messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [{"type": "tool_result", "tool_use_id": tool_use.id, "content": result}],
})

# Step 4: the model uses the result to answer
print("\nSTEP 4: call again; the model answers using the result")
response = client.messages.create(model=MODEL, max_tokens=16000, tools=tools, messages=messages)
show(response)
