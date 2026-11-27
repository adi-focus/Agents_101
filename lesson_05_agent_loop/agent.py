"""Lesson 5 assignment: your first agent.

Run:  python3 agent.py
      python3 agent.py "your own mission here"

The tools are ready. Your job is the loop in run_agent() (exercises 1-3), then
read_file (exercise 5) and human approval (exercise 6).
"""
import json
import pathlib
import sys

import anthropic
import requests

MODEL = "claude-opus-5-5"
client = anthropic.Anthropic()

# The agent can only read and write files inside this folder.
WORKSPACE = pathlib.Path(__file__).parent / "agent_workspace"
WORKSPACE.mkdir(exist_ok=True)

DEFAULT_MISSION = (
    "Which of Lisbon, Cairo and Tokyo will have the highest maximum temperature tomorrow? "
    "Write a short picnic recommendation to picnic.md, including the numbers you used."
)

SYSTEM = (
    "You are a helpful agent that completes missions using the tools provided. "
    "Work step by step. When the mission is complete, reply with a one-paragraph "
    "summary of what you did and found."
)


# =============================================================================
# Tools: ordinary Python functions
# =============================================================================
def get_coordinates(city: str) -> str:
    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1}, timeout=30,
    )
    response.raise_for_status()
    results = response.json().get("results")
    if not results:
        raise ValueError(f"No place found called {city!r}. Check the spelling.")
    top = results[0]
    return json.dumps({
        "name": top["name"], "country": top.get("country", ""),
        "latitude": top["latitude"], "longitude": top["longitude"],
    })


def get_forecast(latitude: float, longitude: float, days: int = 3) -> str:
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude, "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "forecast_days": max(1, min(days, 7)),
            "timezone": "auto",
        },
        timeout=30,
    )
    response.raise_for_status()
    daily = response.json()["daily"]
    # One line per day is easier for the model to read than nested arrays
    rows = [
        {"date": d, "max_c": hi, "min_c": lo, "rain_chance_pct": rain}
        for d, hi, lo, rain in zip(daily["time"], daily["temperature_2m_max"],
                                   daily["temperature_2m_min"],
                                   daily["precipitation_probability_max"])
    ]
    return json.dumps(rows)


def _safe_path(filename: str) -> pathlib.Path:
    """Only allow plain filenames inside WORKSPACE: no folders, no '..'."""
    path = (WORKSPACE / filename).resolve()
    if path.parent != WORKSPACE.resolve():
        raise ValueError("filename must be a plain name like 'notes.md', with no folders")
    return path


def write_file(filename: str, content: str) -> str:
    # Exercise 6: ask a human before writing. Show the filename and the first
    # few lines of content, then input("Allow? [y/N] "). If they don't type "y",
    # return a message saying the user declined (don't raise an error).
    path = _safe_path(filename)
    path.write_text(content)
    return f"Wrote {len(content)} characters to {filename}"


# Exercise 5: add read_file(filename) here. Use _safe_path. Then add it to
# TOOLS and TOOL_FUNCTIONS below.


# =============================================================================
# Tool descriptions: what the model sees
# =============================================================================
TOOLS = [
    {
        "name": "get_coordinates",
        "description": "Look up the latitude and longitude of a city by name. "
                       "Returns JSON with name, country, latitude and longitude.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. 'Lisbon'"}},
            "required": ["city"],
        },
    },
    {
        "name": "get_forecast",
        "description": "Get the daily weather forecast for a location, starting today. "
                       "Returns a JSON list with one entry per day: date, max_c, min_c, "
                       "rain_chance_pct. Index 0 is today, index 1 is tomorrow.",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "days": {"type": "integer", "description": "Days to fetch, 1-7. Default 3."},
            },
            "required": ["latitude", "longitude"],
        },
    },
    {
        "name": "write_file",
        "description": "Save text to a file in the agent's workspace, overwriting it if it "
                       "exists. Use a plain filename like 'notes.md'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content": {"type": "string", "description": "The full file contents"},
            },
            "required": ["filename", "content"],
        },
    },
]

TOOL_FUNCTIONS = {
    "get_coordinates": get_coordinates,
    "get_forecast": get_forecast,
    "write_file": write_file,
}


def run_tool(tool_use) -> dict:
    """Run one tool_use block. Always returns a tool_result, even on errors."""
    func = TOOL_FUNCTIONS.get(tool_use.name)
    if func is None:
        return {"type": "tool_result", "tool_use_id": tool_use.id,
                "content": f"Error: unknown tool {tool_use.name}", "is_error": True}
    try:
        output = func(**tool_use.input)
        return {"type": "tool_result", "tool_use_id": tool_use.id, "content": output}
    except Exception as e:
        return {"type": "tool_result", "tool_use_id": tool_use.id,
                "content": f"Error: {e}", "is_error": True}


# =============================================================================
# The agent loop: this is yours to write
# =============================================================================
def run_agent(mission: str, max_steps: int = 15) -> str | None:
    messages = [{"role": "user", "content": mission}]

    for step in range(1, max_steps + 1):
        # TODO 1: call client.messages.create with model, max_tokens=16000,
        #         system=SYSTEM, tools=TOOLS and messages

        # TODO 2: append the assistant's reply (response.content, as-is) to messages

        # Exercise 2 (trace): print f"--- step {step} ---" and every text block

        # TODO 3: if stop_reason == "end_turn": the mission is complete.
        #         Return the text of the final reply.

        # TODO 4: if stop_reason == "tool_use":
        #           - run EVERY tool_use block in response.content with run_tool()
        #           - (Exercise 2) print each tool name, its input and the first
        #             200 characters of its result
        #           - append ALL the results in ONE user message
        #           - `continue` to the next step

        # TODO 5: any other stop_reason (max_tokens, refusal, ...): print it
        #         clearly and return None. Don't pretend the mission succeeded.
        raise NotImplementedError("Write the agent loop")

    # Exercise 3: we only get here if the loop ran out of steps.
    print(f"Stopped: hit max_steps={max_steps} before the mission was complete.")
    return None


if __name__ == "__main__":
    mission = " ".join(sys.argv[1:]) or DEFAULT_MISSION
    print(f"MISSION: {mission}\n")
    result = run_agent(mission)
    print("\n=== FINAL ANSWER ===")
    print(result)
