#!/usr/bin/env python3
"""
Self-improving system demo — minimal closed loop.

Architecture (deliberately tiny, no frameworks):
    ask        -> read memory -> build prompt -> call model -> print
    feedback   -> call evaluator -> merge into memory -> persist
    show       -> cat memory.json
    reset      -> restore baseline

Every step is printed so the audience sees the loop, not magic.

Requires: LM Studio running locally with a chat model loaded.
Endpoint:  http://localhost:1234/v1/chat/completions  (OpenAI-compatible)
"""
import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
MEMORY_PATH = ROOT / "memory.json"
BASELINE_PATH = ROOT / "memory.baseline.json"
PLANNER_PROMPT = (ROOT / "prompts" / "planner.txt").read_text(encoding="utf-8")
EVALUATOR_PROMPT = (ROOT / "prompts" / "evaluator.txt").read_text(encoding="utf-8")

LMSTUDIO_URL = os.environ.get("LMSTUDIO_URL", "http://localhost:1234/v1/chat/completions")
LMSTUDIO_MODEL = os.environ.get("LMSTUDIO_MODEL", "phi-4-mini-instruct")
TEMPERATURE = float(os.environ.get("LMSTUDIO_TEMP", "0.4"))
MAX_TOKENS = int(os.environ.get("LMSTUDIO_MAX_TOKENS", "256"))
TIMEOUT_S = int(os.environ.get("LMSTUDIO_TIMEOUT", "60"))


# ---------- pretty output ----------
def banner(label: str) -> None:
    print(f"\n\033[36m── {label} {'─' * (60 - len(label))}\033[0m")

def kv(label: str, value: str) -> None:
    print(f"  \033[90m{label}:\033[0m {value}")


def strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks emitted by reasoning models."""
    while "<think>" in text and "</think>" in text:
        start = text.find("<think>")
        end = text.find("</think>") + len("</think>")
        text = (text[:start] + text[end:]).strip()
    return text.strip()


# ---------- model call ----------
def call_model(system: str, user: str, *, json_mode: bool = False) -> str:
    payload = {
        "model": LMSTUDIO_MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.3,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if json_mode:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "memory_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "likes":       {"type": "array", "items": {"type": "string"}},
                        "dislikes":    {"type": "array", "items": {"type": "string"}},
                        "constraints": {"type": "array", "items": {"type": "string"}},
                        "notes":       {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["likes", "dislikes", "constraints", "notes"],
                },
            },
        }
        payload["temperature"] = 0  # evaluator MUST be deterministic
        payload["frequency_penalty"] = 0
        payload["presence_penalty"] = 0

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LMSTUDIO_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        sys.exit(
            f"\n[ERROR] LM Studio rejected the request: HTTP {exc.code}\n"
            f"        URL: {LMSTUDIO_URL}\n"
            f"        Body: {detail[:500]}"
        )
    except urllib.error.URLError as exc:
        sys.exit(f"\n[ERROR] Could not reach LM Studio at {LMSTUDIO_URL}\n        {exc}")
    except TimeoutError:
        sys.exit(
            f"\n[ERROR] Model call timed out after {TIMEOUT_S}s.\n"
            f"        Likely a reasoning model. Switch to a non-reasoning chat model\n"
            f"        (gemma-2-2b-it, llama-3.2-3b-instruct, phi-4-mini-instruct),\n"
            f"        or raise LMSTUDIO_TIMEOUT."
        )
    raw = body["choices"][0]["message"]["content"]
    return strip_thinking(raw).strip() if not json_mode else raw.strip()


# ---------- memory ----------
def load_memory() -> dict:
    if not MEMORY_PATH.exists():
        shutil.copy(BASELINE_PATH, MEMORY_PATH)
    return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))

def save_memory(mem: dict) -> None:
    MEMORY_PATH.write_text(json.dumps(mem, indent=2) + "\n", encoding="utf-8")

def format_memory_block(mem: dict) -> str:
    prefs = mem.get("preferences", {})
    likes = prefs.get("likes", [])
    dislikes = prefs.get("dislikes", [])
    constraints = mem.get("constraints", [])
    notes = mem.get("notes", [])
    if not any([likes, dislikes, constraints, notes]):
        return "(empty — no preferences known yet)"
    lines = []
    if likes:       lines.append(f"likes:       {', '.join(likes)}")
    if dislikes:    lines.append(f"dislikes:    {', '.join(dislikes)}")
    if constraints: lines.append(f"constraints: {', '.join(constraints)}")
    if notes:       lines.append(f"notes:       {', '.join(notes)}")
    return "\n".join(lines)

def merge_extraction(mem: dict, extracted: dict) -> dict:
    """Union merge — additive only, no forgetting in this demo."""
    def add(target: list, items):
        for item in items or []:
            item = item.strip().lower()
            if item and item not in target:
                target.append(item)
    add(mem["preferences"]["likes"], extracted.get("likes"))
    add(mem["preferences"]["dislikes"], extracted.get("dislikes"))
    add(mem["constraints"], extracted.get("constraints"))
    add(mem["notes"], extracted.get("notes"))
    return mem


# ---------- commands ----------
def cmd_ask(question: str) -> None:
    banner("STEP 1/4  LOAD MEMORY")
    mem = load_memory()
    print(format_memory_block(mem))

    banner("STEP 2/4  CONSTRUCT PROMPT")
    system = PLANNER_PROMPT.replace("{memory_block}", format_memory_block(mem))
    kv("system", f"{len(system)} chars (planner template + memory)")
    kv("user", question)

    banner("STEP 3/4  CALL MODEL")
    kv("endpoint", LMSTUDIO_URL)
    kv("temperature", str(TEMPERATURE))
    answer = call_model(system, question)

    banner("STEP 4/4  RESPONSE")
    print(answer)
    print()


def cmd_feedback(text: str) -> None:
    banner("STEP 1/4  RECEIVE FEEDBACK")
    print(text)

    banner("STEP 2/4  CALL EVALUATOR")
    kv("endpoint", LMSTUDIO_URL)
    kv("mode", "json_object")
    raw = call_model(EVALUATOR_PROMPT, text, json_mode=True)
    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try to recover from accidental fences / prose
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            extracted = json.loads(raw[start:end + 1])
        else:
            sys.exit(f"[ERROR] Evaluator did not return JSON:\n{raw}")

    banner("STEP 3/4  EXTRACTED")
    print(json.dumps(extracted, indent=2))

    banner("STEP 4/4  MERGE INTO MEMORY")
    mem = load_memory()
    before = json.dumps(mem, sort_keys=True)
    mem = merge_extraction(mem, extracted)
    after = json.dumps(mem, sort_keys=True)
    save_memory(mem)
    if before == after:
        print("(no new state — memory unchanged)")
    else:
        print(json.dumps(mem, indent=2))
    print()


def cmd_show() -> None:
    banner("CURRENT MEMORY")
    print(MEMORY_PATH)
    print(json.dumps(load_memory(), indent=2))
    print()


def cmd_reset() -> None:
    shutil.copy(BASELINE_PATH, MEMORY_PATH)
    banner("MEMORY RESET")
    print(f"  restored from {BASELINE_PATH.name}")
    print()


# ---------- entry ----------
def main() -> None:
    p = argparse.ArgumentParser(description="Self-improving system demo")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ask = sub.add_parser("ask", help="Ask the planner a question")
    p_ask.add_argument("question", nargs="+")

    p_fb = sub.add_parser("feedback", help="Give feedback; updates memory")
    p_fb.add_argument("text", nargs="+")

    sub.add_parser("show", help="Show current memory")
    sub.add_parser("reset", help="Reset memory to baseline")

    args = p.parse_args()
    if args.cmd == "ask":
        cmd_ask(" ".join(args.question))
    elif args.cmd == "feedback":
        cmd_feedback(" ".join(args.text))
    elif args.cmd == "show":
        cmd_show()
    elif args.cmd == "reset":
        cmd_reset()


if __name__ == "__main__":
    main()
