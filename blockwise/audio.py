"""Optional extra: render a plan as role notes (one pitch per element kind).

The sound carries only the sequence of element kinds; names, conditions and
nesting are not audible. It is a presentation aid, never a check.
"""

import hashlib
import math
import struct
import wave

from .schema import NOTES, validate_score

SAMPLE_RATE = 8000
BEAT_SECONDS = 0.32


def flatten_events(score):
    score = validate_score(score)
    events = []

    def add(module, function, node, depth, scope):
        kind = node["kind"]
        events.append({"module": module, "function": function, "kind": kind,
                       "note": NOTES[kind], "start_seconds": round(len(events) * BEAT_SECONDS, 3),
                       "duration_seconds": BEAT_SECONDS, "depth": depth, "scope": scope,
                       "metadata": node})

    def traverse(module, function, body, depth, scope):
        for index, node in enumerate(body):
            address = scope + f"/{index}"
            add(module, function, node, depth, address)
            if node["kind"] in ("branch", "loop"):
                traverse(module, function, node["body"], depth + 1, address + "/body")
            if node["kind"] == "branch":
                traverse(module, function, node["otherwise"], depth + 1, address + "/otherwise")

    for module in score["modules"]:
        for function in module["functions"]:
            add(module["path"], function["name"], {"kind": "function", **function}, 0, "function")
            traverse(module["path"], function["name"], function["body"], 1, "body")
    return events


def render_score(score, path):
    events = flatten_events(score)
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        for event in events:
            frequency = 440 * 2 ** ((event["note"] - 69) / 12)
            harmonic = 1 + hashlib.sha256(event["module"].encode()).digest()[0] % 3
            samples = []
            for frame in range(round(SAMPLE_RATE * BEAT_SECONDS)):
                local = frame / SAMPLE_RATE
                envelope = max(0, min(1, local / 0.008, (0.26 - local) / 0.025))
                value = (math.sin(2 * math.pi * frequency * local) * 0.28
                         + math.sin(2 * math.pi * frequency * harmonic * local) * 0.05) * envelope
                samples.append(struct.pack("<h", round(value * 32767)))
            audio.writeframes(b"".join(samples))
    return events

