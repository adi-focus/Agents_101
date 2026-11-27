"""Lesson 2 bonus: the same kind of call, to OpenAI instead of Anthropic.

Compare this file with raw_http.py, line by line. Different company, different
URL, slightly different field names, but the same idea: POST some JSON with
your key in a header, get JSON back.

Run:  python3 openai_example.py
Needs: an OpenAI key in key.yaml at the course root (the file is just the key).

Every API call has three parts, each labelled below:
  1. ENDPOINT  where the request goes (method + URL)
  2. AUTH      how you prove who you are (the key, sent in a header)
  3. SCHEMA    the shape of the JSON you send, and the shape you get back
"""
import json
import pathlib

import requests
import yaml

MODEL = "gpt-6.1-terra"

# =============================================================================
# 1. ENDPOINT
# =============================================================================
#
#   POST https://api.openai.com/v1/responses
#   └┬─┘ └──────────┬─────────┘└┬┘└───┬───┘
#  method       base URL   version  path (which service)
#
# - POST, not GET: we're sending a body (the input) to be processed.
# - This is OpenAI's Responses API, the current way to call their models.
#   (The older /v1/chat/completions endpoint still works, but new code uses this one.)
# - Anthropic's equivalent: POST https://api.anthropic.com/v1/messages
ENDPOINT = "https://api.openai.com/v1/responses"


# =============================================================================
# 2. AUTH (the API key)
# =============================================================================
#
# OpenAI uses a "Bearer token": your key goes in the Authorization header.
#
#   Authorization: Bearer sk-proj-AbC123...
#                  └─┬──┘ └──────┬───────┘
#               scheme      your secret key
#
# - "Bearer" means "whoever bears (holds) this token is allowed in". That's
#   why a leaked key is dangerous: anyone holding it can spend your money.
# - A missing or wrong key returns HTTP 401 Unauthorized (lesson 1, section 3).
# - Anthropic uses its own header instead:  x-api-key: sk-ant-...
#   (plus an anthropic-version header saying which version of the API to use)
#
# Here the key is read from key.yaml. The file can be just the key on one line,
# or `openai_api_key: sk-...`. Never print the key or commit this file.
KEY_FILE = pathlib.Path(__file__).resolve().parent.parent / "key.yaml"
data = yaml.safe_load(KEY_FILE.read_text())
api_key = data if isinstance(data, str) else data["openai_api_key"]

HEADERS = {
    "Authorization": f"Bearer {api_key}",   # AUTH: who you are
    "Content-Type": "application/json",     # "the body I'm sending is JSON"
}


# =============================================================================
# 3a. REQUEST SCHEMA (what you send)
# =============================================================================
#
#   {
#     "model":        string,            REQUIRED  which model answers
#     "input":        string | [...],    REQUIRED  either one string, or a list of
#                                                  messages: [{"role": "user", "content": "..."}, ...]
#     "instructions": string,            optional  the system prompt
#     "max_output_tokens": int,          optional  ceiling on the reply's length
#     "tools":        [...],             optional  functions the model may ask to call (lesson 4)
#     "stream":       bool,              optional  send the reply word by word
#     "store":        bool,              optional  keep this response on OpenAI's servers (default: true)
#     "previous_response_id": string     optional  continue an earlier stored response
#   }
#
# Differences from Anthropic's request schema:
# - "input" instead of "messages", and it can be a plain string.
# - "instructions" instead of "system".
# - Anthropic requires "max_tokens"; here the length limit is optional.
# - Memory: lesson 3 says the API is stateless and you resend the history.
#   That's true for Anthropic. The Responses API can instead store the
#   conversation for you: pass "previous_response_id" and it picks up where
#   that response left off. Resending the history yourself works here too.
REQUEST_BODY = {
    "model": MODEL,
    "input": "Explain what an API is in one sentence.",
}


# =============================================================================
# Send it: ENDPOINT + AUTH (headers) + SCHEMA (json body)
# =============================================================================
response = requests.post(ENDPOINT, headers=HEADERS, json=REQUEST_BODY, timeout=120)

print("Status code:", response.status_code)   # 200 OK · 400 bad body · 401 bad key · 429 too many requests
body = response.json()

# The full body is long: it repeats every setting back to you (temperature,
# tools, reasoning, ...). Print just the parts this lesson is about.
# To see everything, use: print(json.dumps(body, indent=2))
print(json.dumps({k: body.get(k) for k in ("id", "status", "model", "output", "usage", "error")}, indent=2))


# =============================================================================
# 3b. RESPONSE SCHEMA (what you get back), trimmed to the important fields
# =============================================================================
#
#   {
#     "id":     "resp_088ec...",          unique ID (pass as previous_response_id to continue)
#     "object": "response",
#     "status": "completed",              "completed" | "incomplete" | "failed"
#     "model":  "gpt-6.1-terra",
#     "output": [                         a LIST of typed items (like Anthropic's content blocks)
#       {
#         "type":   "message",            other types: "reasoning", "function_call" (lesson 4)
#         "role":   "assistant",
#         "status": "completed",
#         "content": [
#           {
#             "type": "output_text",
#             "text": "An API is ..."    <- THE ANSWER
#           }
#         ]
#       }
#     ],
#     "incomplete_details": null,         if status is "incomplete", this says why,
#                                         e.g. {"reason": "max_output_tokens"}
#     "usage": {                          what you're billed for
#       "input_tokens":  25,
#       "output_tokens": 22,
#       "total_tokens":  47
#     },
#     "error": null
#   }
#
# If something goes wrong (status 4xx/5xx), the body is an error instead:
#
#   {"error": {"message": "Incorrect API key provided...", "type": "...", "code": "invalid_api_key"}}
#
# As with Claude, the output is a LIST of items, and the first one isn't
# always the text (a "reasoning" item can come first). Loop over it and check
# each item's "type", the same rule as lesson 2.
if response.ok:
    texts = [
        part["text"]
        for item in body["output"] if item["type"] == "message"
        for part in item["content"] if part["type"] == "output_text"
    ]
    print("\n=== The useful bits ===")
    print("text:  ", "".join(texts))
    print("status:", body["status"], body.get("incomplete_details") or "")
    print("usage: ", body["usage"]["input_tokens"], "in /", body["usage"]["output_tokens"], "out")
else:
    print("\nError:", body.get("error", {}).get("message"))


# =============================================================================
# Summary: the same three parts, side by side
# =============================================================================
#
#                    Anthropic (raw_http.py)            OpenAI (this file)
#   ENDPOINT         POST /v1/messages                  POST /v1/responses
#   AUTH             x-api-key: <key>                   Authorization: Bearer <key>
#                    + anthropic-version header
#   REQUEST SCHEMA   model, max_tokens (required),      model, input (string or list),
#                    messages, optional system          optional instructions
#   RESPONSE SCHEMA  content[] blocks                   output[] items
#                    → type "text" → .text              → type "message" → content[]
#                                                         → type "output_text" → .text
#   WHY IT STOPPED   stop_reason ("end_turn")           status ("completed") + incomplete_details
#   TOKENS           usage.input/output_tokens          usage.input/output_tokens
#   MEMORY           none: you resend the history       optional: previous_response_id
