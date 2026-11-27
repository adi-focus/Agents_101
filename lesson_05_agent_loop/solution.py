"""Lesson 5 solution. Try agent.py before reading this.

Run:  python3 solution.py
      python3 solution.py "your own mission here"
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
    path = _safe_path(filename)
    # Exercise 6: a human approves before anything is written
    print(f"\n  The agent wants to write {filename!r}:")
    for line in content.splitlines()[:8]:
        print(f"    | {line}")
    if input("  Allow? [y/N] ").strip().lower() != "y":
        return "The user declined this write. The file was not written."
    path.write_text(content)
    return f"Wrote {len(content)} characters to {filename}"


# Exercise 5
def read_file(filename: str) -> str:
    path = _safe_path(filename)
    if not path.exists():
        existing = sorted(p.name for p in WORKSPACE.iterdir()) or ["(empty)"]
        raise FileNotFoundError(f"{filename} does not exist. Files: {', '.join(existing)}")
    return path.read_text()


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
        "name": "read_file",
        "description": "Read a text file from the agent's workspace. Use a plain filename "
                       "like 'notes.md'. If the file doesn't exist, the error lists the "
                       "files that do.",
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string"}},
            "required": ["filename"],
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
    "read_file": read_file,
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
# The agent loop
# =============================================================================
def text_of(response) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


def run_agent(mission: str, max_steps: int = 15) -> str | None:
    messages = [{"role": "user", "content": mission}]

    for step in range(1, max_steps + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        # Trace (exercise 2)
        print(f"--- step {step} (stop_reason={response.stop_reason}, "
              f"in={response.usage.input_tokens} out={response.usage.output_tokens}) ---")
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"  model: {block.text.strip()}")

        if response.stop_reason == "end_turn":
            return text_of(response)

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block)
                    flag = "ERROR " if result.get("is_error") else ""
                    print(f"  tool:  {block.name}({json.dumps(block.input)})")
                    print(f"         -> {flag}{result['content'][:200]}")
                    results.append(result)
            messages.append({"role": "user", "content": results})   # ONE message, all results
            continue

        # max_tokens, refusal, or anything unexpected: stop and say so
        print(f"Stopped early: stop_reason={response.stop_reason!r}")
        return None

    print(f"Stopped: hit max_steps={max_steps} before the mission was complete.")
    return None


# Exercise 4 answer: the loop has no idea what the mission is. It only routes
#   tool requests to functions. All mission-specific "planning" is done by the
#   model, so a new mission needs no new code, as long as the tools can do it.
# Exercise 7 (one answer): an agent is an LLM in a loop with tools. The model
#   decides what to do next; my code carries out those decisions, reports the
#   results back, enforces the limits, and decides when to stop.


if __name__ == "__main__":
    mission = " ".join(sys.argv[1:]) or DEFAULT_MISSION
    print(f"MISSION: {mission}\n")
    result = run_agent(mission)
    print("\n=== FINAL ANSWER ===")
    print(result)
