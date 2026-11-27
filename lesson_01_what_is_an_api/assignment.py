"""Lesson 1 assignment: What is an API?

Work through the exercises in order. Run `python3 assignment.py` after each one.
Write your predictions in notes.md BEFORE you run anything.
"""
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


# =============================================================================
# Exercise 1: Dissect a URL  (no code to run, just fill in the strings)
# =============================================================================
# Here is a URL. Fill in each part below.
#
#   https://api.open-meteo.com/v1/forecast?latitude=35.68&longitude=139.69&current=temperature_2m,wind_speed_10m
#
# TODO: fill these in
METHOD = "???"          # what HTTP method does a browser use when you paste a URL?
BASE_URL = "???"
ENDPOINT = "???"
QUERY_PARAMS = {}       # as a dict, e.g. {"latitude": "35.68", ...}
#
# Then: paste the URL into your browser. Which city is it? What does adding
# `wind_speed_10m` change in the response?


# =============================================================================
# Exercise 2: Break it on purpose  (Predict -> Run -> Explain)
# =============================================================================
# Before running, write in notes.md:
#   a) What status code will latitude=999 return? What will the body say?
#   b) What status code will a misspelled endpoint (/v1/forcast) return?
#   c) Which of the two is "your fault" and which, if any, is "their fault"?
#
# Then set RUN_EXERCISE_2 = True and run the file.
RUN_EXERCISE_2 = False

def exercise_2():
    r1 = requests.get(FORECAST_URL, params={"latitude": 999, "longitude": 0, "current": "temperature_2m"}, timeout=30)
    print("a) latitude=999  ->", r1.status_code, r1.text[:200])
    r2 = requests.get("https://api.open-meteo.com/v1/forcast", params={"latitude": 0, "longitude": 0}, timeout=30)
    print("b) bad endpoint ->", r2.status_code, r2.text[:200])


# =============================================================================
# Exercise 3: get_coordinates(city)
# =============================================================================
# Call the geocoding API:  GET {GEOCODING_URL}?name=<city>&count=1
# Open this in your browser first to see what the response looks like:
#   https://geocoding-api.open-meteo.com/v1/search?name=Lisbon&count=1
#
# Return a dict like {"name": "Lisbon", "country": "Portugal", "latitude": 38.7, "longitude": -9.1}
# If the city doesn't exist, return None. (Hint: look at what the API returns for
# name=Xyzzyville. Is there a "results" key?)

def get_coordinates(city: str) -> dict | None:
    # TODO: make the request with requests.get(..., params=..., timeout=30)
    # TODO: check response.status_code. What should you do if it isn't 200?
    # TODO: pull out the first result, or return None if there are none
    raise NotImplementedError("Exercise 3")


# =============================================================================
# Exercise 4: get_current_temperature(latitude, longitude)
# =============================================================================
# Call the forecast API with current=temperature_2m and return the temperature
# as a float (degrees Celsius).

def get_current_temperature(latitude: float, longitude: float) -> float:
    # TODO
    raise NotImplementedError("Exercise 4")


# =============================================================================
# Exercise 5 (stretch): The warmest city
# =============================================================================
# Use your two functions to find the warmest city in the list. Print each
# city's temperature, then the winner. Skip (and report) cities that aren't found.
#
# Afterwards, answer in notes.md: list the steps your code takes, in order.
# Who decided that order? (In lesson 5, an LLM will decide it.)

CITIES = ["Lisbon", "Cairo", "Tokyo", "Xyzzyville"]

def warmest_city(cities: list[str]) -> None:
    # TODO
    raise NotImplementedError("Exercise 5")


# =============================================================================
if __name__ == "__main__":
    print("Exercise 1:", METHOD, BASE_URL, ENDPOINT, QUERY_PARAMS)

    if RUN_EXERCISE_2:
        exercise_2()

    try:
        print("Exercise 3:", get_coordinates("Lisbon"))
        print("Exercise 3 (missing city):", get_coordinates("Xyzzyville"))
    except NotImplementedError as e:
        print("Not done yet:", e)

    try:
        print("Exercise 4: Lisbon is", get_current_temperature(38.72, -9.14), "°C")
    except NotImplementedError as e:
        print("Not done yet:", e)

    try:
        warmest_city(CITIES)
    except NotImplementedError as e:
        print("Not done yet:", e)
