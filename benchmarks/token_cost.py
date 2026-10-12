"""Estimate what calling a preset costs an agent, compared with writing the same function itself.

usage: python benchmarks/token_cost.py        (pip install tiktoken for real token counts;
                                               otherwise it estimates 4 characters per token)
Counts use an OpenAI tokenizer as a stand-in, so treat them as close estimates, not exact Claude counts.
Output tokens are weighted 5x input tokens, the usual price ratio.
"""

import json
import tempfile

from blockwise.presets import find, load_presets, render, summary
from blockwise.project import apply_preset, function_source

try:
    import tiktoken

    _enc = tiktoken.get_encoding("o200k_base")

    def tokens(text):
        return len(_enc.encode(text))
except ImportError:
    def tokens(text):
        return max(1, round(len(text) / 4))

OUTPUT_WEIGHT = 5


def main():
    presets = load_presets()
    rows = []
    for preset_id, preset in presets.items():
        source, imports = function_source(*render(preset))
        with tempfile.TemporaryDirectory() as project:
            reply = json.dumps(apply_preset(project, preset_id, "app/m.py", {}), separators=(",", ":"))
        write = tokens("\n".join(imports + [source]))
        call, answer = tokens(f"blockwise apply {preset_id} --into app/m.py"), tokens(reply)
        rows.append((preset_id, write, call, answer))
    listing = tokens(json.dumps([summary(p) for p in presets.values()], separators=(",", ":")))
    finding = tokens(json.dumps(find("reject negative number"), separators=(",", ":")))
    n = len(rows)
    write = sum(r[1] for r in rows) / n
    call = sum(r[2] for r in rows) / n
    answer = sum(r[3] for r in rows) / n
    saved = write * OUTPUT_WEIGHT - (call * OUTPUT_WEIGHT + answer)
    print(json.dumps({
        "presets": n,
        "avg_tokens_to_write_function": round(write),
        "avg_tokens_to_call_preset": {"output": round(call), "input_reply": round(answer)},
        "saved_per_use_input_equivalent": round(saved),
        "discovery_cost_input": {"list_all": listing, "find_one_query": finding},
        "break_even_uses": {"with_list": round(listing / saved, 1), "with_find": round(finding / saved, 1)},
    }, indent=2))


if __name__ == "__main__":
    main()
