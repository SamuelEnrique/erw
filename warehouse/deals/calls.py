#!/usr/bin/env python3
"""One model call of the deal and datacenter extractors, retried where a retry can help (session 2237, chain 156).

Energy Research Warehouse (ERW). From 26 to 30 October 2026 both extractors failed every day with the health line
"RuntimeError: all 1 calls failed": the API had answered "You have reached your specified API usage limits. You will
regain access on 2026-11-01 at 00:00 UTC", which only the run log kept (`docs/reviews/deals-audit-2026-11-06.md`, row
A16). `call()` sends one call and sorts what comes back:

- **the spending limit** (the API's "usage limits", "credit balance"): no retry, and `Stop` is raised so the run sends
  no further call; its words go to the health line;
- **a refusal** (`stop_reason` refusal) or an answer that is not the schema's JSON: one retry;
- **a busy or failing API** (429, 500, 502, 503, 529, overloaded, a timeout, a dropped connection): two retries, 10
  and 30 seconds apart (the SDK's own retries come first);
- **anything else**: no retry.

Every failure is raised as `Failed` (or `Stop`) with plain words (`words`), never the class name alone. `sleep` is a
parameter so a test waits for nothing.
"""

import json
import time

WAITS = (10, 30)


class Failed(Exception):
    def __init__(self, words, kind):
        super().__init__(words)
        self.words, self.kind = words, kind


class Stop(Failed):
    """The run should send no further call (the spending limit)."""


def words_of(exc):
    msg = getattr(exc, "message", None) or str(exc)
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        msg = (body.get("error") or {}).get("message") or msg
    return " ".join(str(msg).split())[:300]


def kind_of(exc):
    w = words_of(exc).lower()
    status = getattr(exc, "status_code", None)
    if "usage limit" in w or "credit balance" in w or "spending limit" in w:
        return "limit"
    if "stop_reason refusal" in w or "not json" in w:
        return "refused"
    if status in (429, 500, 502, 503, 529) or "overloaded" in w or "timeout" in w or "timed out" in w \
            or type(exc).__name__ in ("APIConnectionError", "APITimeoutError", "InternalServerError", "RateLimitError"):
        return "busy"
    return "error"


def call(client, kwargs, usage, log, label, sleep=time.sleep):
    """(response, text): the answer of one call whose stop_reason is end_turn and whose text is JSON. usage is the run's
    list; each attempt's tokens are appended (an attempt that answered is paid for, a retry or not)."""
    tries = {"refused": 1, "busy": len(WAITS)}
    used = {"refused": 0, "busy": 0}
    while True:
        try:
            resp = client.messages.create(**kwargs)
            u = resp.usage
            usage.append(dict(input=u.input_tokens, output=u.output_tokens,
                              cache_write=u.cache_creation_input_tokens or 0, cache_read=u.cache_read_input_tokens or 0))
            if resp.stop_reason != "end_turn":
                raise RuntimeError(f"stop_reason {resp.stop_reason}")
            text = "".join(b.text for b in resp.content if b.type == "text")
            try:
                json.loads(text)
            except ValueError:
                raise RuntimeError("the answer is not JSON")
            return resp, text
        except Exception as exc:  # noqa: BLE001
            k, w = kind_of(exc), words_of(exc)
            if k == "limit":
                raise Stop(f"the API's spending limit: {w}", k)
            if k in tries and used[k] < tries[k]:
                wait = WAITS[used[k]] if k == "busy" else 0
                used[k] += 1
                log(f"  {label}: {k} ({w}); retry {used[k]} of {tries[k]}" + (f" in {wait} s" if wait else ""))
                if wait:
                    sleep(wait)
                continue
            raise Failed({"refused": "the model refused or did not answer in the schema", "busy": "the API was busy",
                          "error": "the call failed"}[k] + f": {w}", k)
