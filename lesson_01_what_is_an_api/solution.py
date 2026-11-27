"""Lesson 1 solution. Try the assignment before reading this."""
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Exercise 1
METHOD = "GET"
BASE_URL = "https://api.open-meteo.com"
ENDPOINT = "/v1/forecast"
QUERY_PARAMS = {"latitude": "35.68", "longitude": "139.69", "current": "temperature_2m,wind_speed_10m"}
# It's Tokyo. Adding wind_speed_10m adds a second field under "current" (and its unit under "current_units").

# Exercise 2 answers:
#   a) 400 Bad Request, body like {"error": true, "reason": "Latitude must be in range of -90 to 90°..."}
#   b) 404 Not Found: that endpoint doesn't exist
#   c) Both are 4xx = "your fault". A 5xx would be the server's fault.


# Exercise 3
def get_coordinates(city: str) -> dict | None:
    response = requests.get(GEOCODING_URL, params={"name": city, "count": 1}, timeout=30)
    response.raise_for_status()          # turns a 4xx/5xx into a Python exception
    results = response.json().get("results")   # the key is missing when nothing matches
    if not results:
        return None
    top = results[0]
    return {
        "name": top["name"],
        "country": top.get("country", ""),
        "latitude": top["latitude"],
        "longitude": top["longitude"],
    }


# Exercise 4
def get_current_temperature(latitude: float, longitude: float) -> float:
    response = requests.get(
        FORECAST_URL,
        params={"latitude": latitude, "longitude": longitude, "current": "temperature_2m"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["current"]["temperature_2m"]


# Exercise 5
CITIES = ["Lisbon", "Cairo", "Tokyo", "Xyzzyville"]

def warmest_city(cities: list[str]) -> None:
    temps = {}
    for city in cities:
        place = get_coordinates(city)
        if place is None:
            print(f"  {city}: not found, skipping")
            continue
        temps[city] = get_current_temperature(place["latitude"], place["longitude"])
        print(f"  {city}: {temps[city]} °C")
    if temps:
        winner = max(temps, key=temps.get)
        print(f"Warmest: {winner} ({temps[winner]} °C)")
    # The plan (geocode -> fetch -> compare) was decided by me, the programmer.


if __name__ == "__main__":
    print(get_coordinates("Lisbon"))
    print(get_coordinates("Xyzzyville"))
    warmest_city(CITIES)
