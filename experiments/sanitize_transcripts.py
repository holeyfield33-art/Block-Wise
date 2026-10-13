"""Replace raw sub-agent transcripts with sanitized usage records before publishing.

The raw transcripts include the agent harness's own context (account and session details). For each
`transcript.jsonl` found under the given directories, this writes `usage_records.jsonl` next to it and
deletes the raw file. Each record keeps the measured fields: timestamp, request id, model,
provider-reported usage, and the tool calls made (name, plus the command for Bash).

    python sanitize_transcripts.py trusted-blueprint-002/runs agent-cache-003/runs
"""

import json
import sys
from pathlib import Path


def records(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        message = entry.get("message") or {}
        if message.get("role") != "assistant":
            continue
        tools = []
        for block in message.get("content") or []:
            if block.get("type") == "tool_use":
                call = {"name": block.get("name")}
                if block.get("name") == "Bash":
                    call["command"] = (block.get("input") or {}).get("command", "")
                tools.append(call)
        yield {"timestamp": entry.get("timestamp"), "request_id": entry.get("requestId"), "model": message.get("model"),
               "usage": message.get("usage"), "tool_calls": tools}


def main(dirs):
    for root in dirs:
        for raw in sorted(Path(root).rglob("transcript.jsonl")):
            out = raw.with_name("usage_records.jsonl")
            out.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in records(raw)), encoding="utf-8")
            raw.unlink()
            print(f"{raw} -> {out.name}")


if __name__ == "__main__":
    main(sys.argv[1:])
