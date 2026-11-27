# Lesson 1: What is an API?

**Goal:** by the end of this lesson you can call a web API three ways (browser, terminal, Python),
read every part of the response, and wrap the call in a function you can reuse.

---

## 1. The idea

An **API** (Application Programming Interface) is a way for one program to ask another program
to do something, using an agreed format.

A restaurant is a good comparison:

```
  You (client)  ──── order ────►  Waiter (API)  ──►  Kitchen (server)
                ◄─── food ─────                 ◄──
```

- You don't walk into the kitchen. You use the **menu** (the API's documentation) and place an
  **order** (a request).
- The waiter brings back **food** (a response), or tells you "we're out of that" (an error).
- You don't need to know how the kitchen works. You only need to know how to order.

A **web API** does this over the internet, using **HTTP**, the same protocol your browser uses
to load web pages. The only difference is that the server sends back data, usually **JSON**,
instead of a page meant for people.

## 2. Anatomy of a request

Here is a real request to a free weather API (no key needed):

```
GET https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&current=temperature_2m
```

| Part | In this example | Meaning |
|---|---|---|
| **Method** | `GET` | What you want to do. `GET` = read something. `POST` = send something to be processed. |
| **Base URL** | `https://api.open-meteo.com` | Which server you're talking to. |
| **Endpoint (path)** | `/v1/forecast` | Which service on that server. `v1` is the API version. |
| **Query parameters** | `?latitude=48.85&longitude=2.35&current=temperature_2m` | The details of your order, as `key=value` pairs joined by `&`. |
| **Headers** | *(none needed here)* | Extra information about the request: who you are (API key), what format you're sending. |
| **Body** | *(none for GET)* | Data you send with a `POST`. You'll use it in lesson 2. |

## 3. Anatomy of a response

```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "latitude": 48.86,
  "longitude": 2.34,
  "current_units": {"temperature_2m": "°C"},
  "current": {"time": "2026-11-26T14:00", "temperature_2m": 9.4}
}
```

| Part | Meaning |
|---|---|
| **Status code** | A number that says how it went. Learn these four: `200` OK · `400` you sent something wrong · `401` you're not allowed (bad or missing key) · `500` the server broke. Rule of thumb: **2xx = success, 4xx = your fault, 5xx = their fault.** |
| **Headers** | Information about the response, such as its format (`application/json`). |
| **Body** | The data itself, almost always JSON. |

### JSON in 30 seconds

JSON is text that looks almost exactly like Python dictionaries and lists:

```json
{"name": "Paris", "population": 2100000, "tags": ["capital", "river"], "is_big": true}
```

In Python, `response.json()` turns it into a `dict` you can index:
`data["current"]["temperature_2m"]`.

## 4. Three ways to make the same call

**a) Browser.** Paste the URL into the address bar. You'll see the raw JSON.

**b) Terminal (`curl`):**
```bash
curl "https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&current=temperature_2m"
```

**c) Python (`requests`):**
```python
import requests

response = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={"latitude": 48.85, "longitude": 2.35, "current": "temperature_2m"},
)
print(response.status_code)                     # 200
data = response.json()                          # JSON text -> Python dict
print(data["current"]["temperature_2m"])        # 9.4
```

All three send the same HTTP request. A browser, `curl` and `requests` are all **HTTP clients**.

## 5. API keys

Most APIs need to know who is calling, so they can bill you and stop abuse. You prove who you are
with an **API key**, a long secret string sent in a **header**:

```
x-api-key: sk-ant-...
```

Treat a key like a password. Keep it in an environment variable, never in your code, and never
commit it to git. The weather API in this lesson is free and needs no key. The Claude API in
lesson 2 does.

## 6. Why this matters for agents

An LLM is a server behind an API. Calling Claude is the same kind of HTTP request you make in this
lesson. And an agent's "tools" are mostly ordinary functions that call ordinary APIs, like the
weather function you're about to write. Keep that function: you'll hand it to the model in lesson 4.

---

## Run the examples

```bash
cd lesson_01_what_is_an_api
python3 examples.py
```

## Assignments

Open [`assignment.py`](assignment.py). Exercises 1–2 are Predict → Run → Explain. Exercises 3–5
are code to write. Run the file after each one:

```bash
python3 assignment.py
```

1. **Dissect a URL.** Label each part of a URL with a different city and extra parameters.
2. **Break it on purpose.** Predict the status code and error message for an impossible latitude
   (`999`), then for a misspelled endpoint. Run both.
3. **`get_coordinates(city)`.** Use the geocoding API to turn a city name into latitude and
   longitude. Handle a city that doesn't exist.
4. **`get_current_temperature(lat, lon)`.** Return the current temperature as a number.
5. **Stretch: the warmest city.** Given a list of cities, print the warmest. Notice that *you*
   wrote every step of the plan. In lesson 5, the model writes the plan.

**Done when:** `python3 assignment.py` prints the temperature for three cities and names the
warmest, without crashing on a made-up city name.
