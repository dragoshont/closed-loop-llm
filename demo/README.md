# demo/

The runnable closed-loop demo. **All setup, usage, troubleshooting, and
configuration docs live in the [top-level README](../README.md).**

## Files

| File | Role |
|---|---|
| `demo.py` | CLI — `ask` / `feedback` / `show` / `reset`. ~170 lines of stdlib Python. |
| `prompts/planner.txt` | System prompt that consumes `{memory_block}` and answers the user. |
| `prompts/evaluator.txt` | System prompt that extracts structured preferences from feedback. |
| `memory.baseline.json` | Empty state — `reset` copies this over `memory.json`. |
| `memory.json` | The persistent state. Generated on first run, gitignored. |
| `reset.ps1` | PowerShell helper for resetting memory between runs. |

## Quick reference

```text
python demo.py reset
python demo.py ask      "Suggest something fun for this weekend"
python demo.py feedback "I dislike outdoor activities and I'm on a tight budget"
python demo.py ask      "Suggest something fun for this weekend"
python demo.py show
```

See the [top-level README](../README.md) for install, platform-specific runtime
selection, the model recommendation, environment variables, troubleshooting,
and the architecture diagram.
