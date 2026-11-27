"""Lesson 2: calling Claude with plain HTTP. No SDK, just `requests`, like lesson 1.

You won't write code like this day to day (lesson 3 onward uses the SDK), but it
shows that an LLM is just a server you send JSON to.

Run:  python3 raw_http.py
"""
import json
import os

import requests

MODEL = "claude-opus-5-5"

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise SystemExit("Set ANTHROPIC_API_KEY first (see the course README).")

response = requests.post(
    "https://api.anthropic.com/v1/messages",            # base URL + endpoint
    headers={
        "x-api-key": api_key,                           # who you are
        "anthropic-version": "2026-10-21",              # which API version's rules to use
        "content-type": "application/json",             # the body is JSON
    },
    json={                                              # the body
        "model": MODEL,
        "max_tokens": 16000,
        "messages": [
            {"role": "user", "content": "Explain what an API is in one sentence."}
        ],
    },
    timeout=120,
)

print("Status code:", response.status_code)
print(json.dumps(response.json(), indent=2))
