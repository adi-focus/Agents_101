"""Lesson 1 examples: calling a web API from Python.

Run:  python3 examples.py
No API key needed. Open-Meteo is free.
"""
import json

import requests

# --- Example 1: the simplest possible GET request ----------------------------
response = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={"latitude": 48.85, "longitude": 2.35, "current": "temperature_2m"},
    timeout=30,
)

print("=== Example 1: the full request and response ===")
print("URL that was actually sent:", response.url)   # requests built the ?a=b&c=d part for you
print("Status code:", response.status_code)
print("Content-Type header:", response.headers.get("Content-Type"))
print("Raw body (text):", response.text[:200], "...")

# --- Example 2: JSON body -> Python dict -------------------------------------
data = response.json()
print("\n=== Example 2: the body as a Python dict ===")
print(json.dumps(data, indent=2))   # pretty-print so you can see the structure
print("Paris right now:", data["current"]["temperature_2m"], data["current_units"]["temperature_2m"])

# --- Example 3: a second API (geocoding: city name -> coordinates) -----------
geo = requests.get(
    "https://geocoding-api.open-meteo.com/v1/search",
    params={"name": "Tokyo", "count": 1},
    timeout=30,
).json()
print("\n=== Example 3: geocoding ===")
first = geo["results"][0]
print(f"{first['name']}, {first['country']}: lat={first['latitude']}, lon={first['longitude']}")

# --- Example 4: an error response --------------------------------------------
bad = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={"latitude": 999, "longitude": 2.35, "current": "temperature_2m"},
    timeout=30,
)
print("\n=== Example 4: what an error looks like ===")
print("Status code:", bad.status_code)
print("Body:", bad.text)
