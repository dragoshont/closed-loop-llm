# closed-loop-llm

A tiny, transparent example of a self-improving LLM system. The model never
changes — the **memory** does. Companion code for the talk **"Designing
Self-Improving Systems with LLMs."**

```
ask → evaluate → persist → adapt → ask
```

## The loop, in commands

After the [setup](#setup-5-minutes), the entire demo is four commands:

```text
demo.py reset
demo.py ask      "Suggest something fun for this weekend"
demo.py feedback "I dislike outdoor activities and I'm on a tight budget"
demo.py ask      "Suggest something fun for this weekend"
```

**Expected behavior shift** (wording will vary — temperature is `0.4`):

| Step | Memory state | Sample response |
|---|---|---|
| Ask #1 | empty | "Consider trying an **outdoor adventure like hiking**..." |
| Feedback | — | evaluator extracts `dislikes: outdoor activities`, `constraints: tight budget` |
| Ask #2 | populated | "Consider exploring your local **library's digital resources** — **it's free** and can be done **from home**..." |

That shift — same prompt in, different category of answer out, *because the
memory changed and the prompt template re-rendered* — is the whole demo.
No vector DB. No LangChain. No frameworks. No fine-tuning. ~170 lines of
stdlib Python and two prompt files.

> Run the commands using your platform's Python launcher (e.g. `python demo.py …`,
> `python3 demo.py …`, or `py .\demo.py …` on Windows) from inside the `demo/`
> folder. The default model id matches the recommended setup below. If you load
> a different model, set the `LMSTUDIO_MODEL` environment variable — see
> [Configuration](#configuration).

## What this demo shows (and what it deliberately doesn't)

It's worth being precise: this demo proves the **mechanism**, not the
**improvement**.

**What it shows:**

- A closed loop with persistent state external to the model
- An evaluator that turns unstructured feedback into structured memory
- Behavioral change at the orchestration layer, without touching weights
- That all of the above fits in a folder you can `cat`

**What it deliberately doesn't show:**

- Convergence toward a goal over many turns
- A quality metric that improves with iteration
- Anything that could be called "learning" in the rigorous sense

That distinction is the talk's point. *Adaptation* (this demo) plus a
*goal-aligned evaluator* (e.g. [karpathy/autoresearch](https://github.com/karpathy/autoresearch)'s
`val_bpb` + keep-or-discard rule) is what produces *improvement*. This repo
is the substrate; goal-aligned scoring is what you'd add on top to make a
system that genuinely gets better at something measurable.

The talk's central claim:

> Retrieval alone is not self-improvement. Behavioral adaptation is.

This demo is the smallest possible artifact of that second clause.

---

## Repo layout

```
.
├── README.md                    ← you are here (full setup + run + troubleshooting)
├── demo/                        ← the runnable demo
│   ├── demo.py                  ← CLI: ask / feedback / show / reset
│   ├── prompts/
│   │   ├── planner.txt          ← system prompt that consumes {memory_block}
│   │   └── evaluator.txt        ← system prompt that returns strict JSON
│   ├── memory.baseline.json     ← reset target (empty state)
│   └── reset.ps1                ← PowerShell helper for resetting memory
├── slides/                      ← talk slide deck (open index.html in any browser)
│   └── index.html               ← self-contained HTML, no dependencies
└── talk/                        ← talk content (read-only, not needed to run)
    ├── agenda.md                ← 25-min talk + 5-min Q&A timing plan
    ├── core_thesis.md
    ├── audience_takeaways.md
    ├── objections_and_answers.md
    └── demo_script.md
```

---

## Setup (5 minutes)

### 1. Install LM Studio

**LM Studio is free and available on macOS, Windows, and Linux.** Download the
current version from **[lmstudio.ai](https://lmstudio.ai)**. The website
auto-detects your platform; the downloads page also lists every variant:

- **macOS** (Apple Silicon **and** Intel) — `.dmg`, universal binary, drag to `/Applications`
- **Windows x64** (Intel/AMD) — `.exe` installer
- **Windows ARM64** (Snapdragon X) — `.exe` installer whose filename contains
  `arm64`. The x64 build does **not** run natively under emulation.
- **Linux x64** — `.AppImage`, `chmod +x` and run

> ⚠️ **LM Studio ≤ 0.4.13 will not work.** The demo uses the `json_schema`
> response format, which older builds don't support, and the Phi-4 chat
> template needs a recent runtime. Upgrade if you have an older install.

### 2. Pick a chat runtime

Open **Settings → Runtime**. In the **GGUF** dropdown at the top, pick the
runtime marked **compatible** with your hardware:

| Platform | Hardware | Pick this runtime |
|---|---|---|
| **macOS** | Apple Silicon (M1/M2/M3/M4) | `Metal llama.cpp (macOS Apple Silicon)` |
| **macOS** | Intel Mac | `CPU llama.cpp (macOS)` |
| **Windows** | Snapdragon X / ARM64 | `CPU llama.cpp (Windows ARM)` |
| **Windows** | Intel/AMD CPU, no GPU | `CPU llama.cpp (Windows)` |
| **Windows** | NVIDIA GPU | `CUDA llama.cpp (Windows)` |
| **Windows** | Other GPUs (Intel Arc, AMD Radeon) | `Vulkan llama.cpp (Windows)` |
| **Linux** | NVIDIA GPU | `CUDA llama.cpp (Linux)` |
| **Linux** | Other GPUs / CPU only | `Vulkan llama.cpp (Linux)` or `CPU llama.cpp (Linux)` |

LM Studio marks the runtimes that match your machine with **"Latest version"**
in green. Anything marked **"Non Compatible"** in red will fail — don't pick
those even if they sound faster.

> **Why this matters:** picking the wrong runtime is the #1 cause of broken
> demos (degenerate output, "not a valid Win32 application" errors, missing
> chat templates). The compatible runtime for your hardware is the only
> correct answer.

### 3. Download a model

In LM Studio's **Discover** tab, search for and download:

- **`Phi-4-mini-instruct`** (Q4_K_M) — ~2.5 GB, validated for this demo, Microsoft, fast.

Alternatives that should also work:

- `Llama-3.2-3B-Instruct` — Meta, very fast, well-tested
- `Qwen2.5-3B-Instruct` — Alibaba, multilingual

> Avoid **reasoning** variants (`phi-4-mini-reasoning`, `deepseek-r1-distill`,
> etc.) — they emit long `<think>...</think>` blocks that blow past the demo's
> latency budget.

### 4. Start the local server

In LM Studio's **Local Server** tab:

1. Click **Load Model** → pick your downloaded model.
2. Confirm **Reachable at: `http://127.0.0.1:1234`**.
3. Toggle **Status** to **Running**.

Sanity-check the server is up:

```text
GET http://localhost:1234/v1/models
```

It should return JSON listing your loaded model.

### 5. Python

Python **3.10 or newer**. Stdlib only — no `pip install` needed.

---

## Run it

Clone, `cd` into the demo folder, and run the loop:

```text
git clone https://github.com/dragoshont/closed-loop-llm.git
cd closed-loop-llm/demo

python demo.py reset
python demo.py ask      "Suggest something fun for this weekend"
python demo.py feedback "I dislike outdoor activities and I'm on a tight budget"
python demo.py ask      "Suggest something fun for this weekend"
python demo.py show
```

Use `python` / `python3` / `py` per your platform.

---

## Configuration

All optional. Set as environment variables before running `demo.py`. The
default `LMSTUDIO_MODEL` matches the recommended Phi-4-mini-instruct setup
above; only change it if you loaded a different model.

| Variable | Default | What it does |
|---|---|---|
| `LMSTUDIO_URL` | `http://localhost:1234/v1/chat/completions` | OpenAI-compatible endpoint |
| `LMSTUDIO_MODEL` | `phi-4-mini-instruct` | Loaded model id — change if you use a different model |
| `LMSTUDIO_TEMP` | `0.4` | Planner temperature. Evaluator is always `0`. |
| `LMSTUDIO_MAX_TOKENS` | `256` | Caps response length — keeps demo snappy |
| `LMSTUDIO_TIMEOUT` | `60` | Seconds before giving up on a slow model |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `HTTP 400 ... Invalid model identifier` | Loaded model id doesn't match `LMSTUDIO_MODEL` | Either load `phi-4-mini-instruct` in LM Studio, or set `LMSTUDIO_MODEL` to the model you did load |
| `HTTP 400 ... 'response_format.type' must be 'json_schema' or 'text'` | LM Studio version too old | Upgrade LM Studio |
| Output is coherent at first, then degenerates into `/A/B/C/D/...` token salad | Wrong runtime for your hardware | Pick the runtime marked compatible — see runtime table |
| `not a valid Win32 application` (Windows) | x64 runtime on ARM64 machine | Install the ARM64 LM Studio build |
| `Could not reach LM Studio` / connection refused | Server isn't running | Toggle **Status → Running** in the Local Server tab |
| `Model call timed out after 60s` | Reasoning model (`<think>` chains) | Switch to a non-reasoning model, or raise `LMSTUDIO_TIMEOUT` |
| Evaluator returns empty arrays even for clear feedback | Model is too small (under 2B params) | Use a 3B+ instruct model |
| First call after model load is slow | Cold-start warm-up | Pre-warm by running one `ask` before walking on stage |

---

## How the loop actually works

```
                 ┌───────────────────────────┐
                 │     memory.json           │
                 │     (preferences, etc.)   │
                 └──────────┬────────────────┘
                            │
              load          │           merge
                            ▼
   ┌──────────┐      ┌─────────────────┐      ┌─────────────────┐
   │  user    │─────▶│  PLANNER PROMPT │─────▶│      MODEL      │─────▶ answer
   │ question │      │ (template +     │      │  (LM Studio)    │
   └──────────┘      │  memory_block)  │      └─────────────────┘
                     └─────────────────┘
                                                       ▲
                                                       │
   ┌──────────┐      ┌─────────────────┐      ┌─────────────────┐
   │  user    │─────▶│ EVALUATOR PROMPT│─────▶│      MODEL      │─────▶ JSON
   │ feedback │      │ (strict schema) │      │  (LM Studio)    │       (extracted prefs)
   └──────────┘      └─────────────────┘      └─────────────────┘
```

The model never changes. The **prompt** changes — because the **memory** it
embeds changes. That is "system-level learning" in the smallest possible form.

---

## Hacking on it

Things to change to explore the architecture:

- **The evaluator prompt** (`demo/prompts/evaluator.txt`) — try extracting
  different fields. The JSON schema in `demo.py` must match.
- **The planner prompt** (`demo/prompts/planner.txt`) — try a different domain
  (meal planner, code reviewer, support agent). The loop stays identical.
- **The merge logic** (`merge_extraction` in `demo.py`) — currently union-only.
  Add forgetting, conflict resolution, or recency weighting and watch behavior
  shift over many turns.
- **The model** — swap to a smaller/larger instruct model and observe how
  evaluator JSON quality changes. This is the talk's "evaluators are
  load-bearing" point made tangible.

---

## The thesis in one line

> Modern AI systems improve primarily through feedback orchestration, memory,
> evaluators, telemetry, and runtime adaptation — **not** through continuous
> retraining of model weights.

The talk argues the **model is increasingly becoming the least interesting
component**. This repo exists to make the *adaptation* half of that claim
runnable on your laptop in under five minutes. The *improvement* half lives
one layer up — see ["What this demo shows (and what it deliberately doesn't)"](#what-this-demo-shows-and-what-it-deliberately-doesnt).

For the full argument see [`talk/core_thesis.md`](./talk/core_thesis.md) and
[`talk/audience_takeaways.md`](./talk/audience_takeaways.md). For pre-emptive
answers to the usual skeptics' questions ("isn't this just RAG?", "isn't this
just chat history?"), see [`talk/objections_and_answers.md`](./talk/objections_and_answers.md).
For the on-stage choreography see [`talk/demo_script.md`](./talk/demo_script.md).

---

## License

Treat as MIT — copy, fork, present, modify, share.
