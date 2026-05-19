# closed-loop-llm

A tiny, transparent example of a self-improving LLM system. The model never
changes — the **memory** does. Companion code for the talk **"Designing
Self-Improving Systems with LLMs."**

```
ask → evaluate → persist → adapt → ask
```

**What you'll see in 3 commands:**

1. Ask a generic question → get a generic answer.
2. Give a piece of feedback → an evaluator extracts structured preferences into `memory.json`.
3. Ask the same question again → different answer. Same model. Same temperature.

No vector DB. No LangChain. No frameworks. No fine-tuning. ~170 lines of
stdlib Python and two prompt files. That is the entire point.

---

## Try it

### 1. Install LM Studio (free, macOS / Windows / Linux)

Download the current build from **[lmstudio.ai](https://lmstudio.ai)**. The
website auto-detects your platform. Available for:

- **macOS** — Apple Silicon and Intel
- **Windows** — x64 (Intel/AMD) and ARM64 (Snapdragon X)
- **Linux** — x64 AppImage

> ⚠️ LM Studio 0.4.13 or older won't work — upgrade if you have an older install.

### 2. Pick a chat runtime

In LM Studio, open **Settings → Runtime** and set the **GGUF** dropdown to the
runtime marked compatible with your hardware (Metal on Apple Silicon, CPU on
Snapdragon X, CUDA on NVIDIA, etc.). The full lookup table lives in the
[demo README](./demo/README.md#2-pick-a-chat-runtime).

### 3. Download a model

In LM Studio's **Discover** tab, download **`Phi-4-mini-instruct`** (Q4_K_M,
~2.5 GB). Microsoft, non-reasoning, fast. Alternatives that work:
`Llama-3.2-3B-Instruct`, `Qwen2.5-3B-Instruct`.

### 4. Start the local server

In LM Studio's **Local Server** tab, load the model and toggle **Status →
Running** (default port 1234).

### 5. Run the demo

```text
git clone https://github.com/dragoshont/closed-loop-llm.git
cd closed-loop-llm/demo

# Reset memory
python demo.py reset

# First ask — empty memory, generic answer
python demo.py ask "Suggest something fun for this weekend"

# Feedback — evaluator extracts structured prefs into memory.json
python demo.py feedback "I dislike outdoor activities and I'm on a tight budget"

# Second ask — same prompt, different answer
python demo.py ask "Suggest something fun for this weekend"

# Inspect persistent state
python demo.py show
```

Use `python` / `python3` / `py` per your platform. Requires Python 3.10+.

That's it. The behavior shift between the two asks — without retraining
anything — is the talk's central claim, made provable in 30 seconds.

For platform-specific runtime details, troubleshooting, configuration knobs,
and "what to point at on stage," see [`demo/README.md`](./demo/README.md).

---

## Repo layout

```
.
├── README.md            ← you are here
├── demo/                ← the runnable demo
│   ├── README.md        ← detailed setup, troubleshooting, hacking
│   ├── demo.py          ← CLI: ask / feedback / show / reset
│   ├── prompts/         ← planner + evaluator system prompts
│   ├── memory.baseline.json
│   └── reset.ps1
└── talk/                ← talk content (read-only, not needed to run the demo)
    ├── core_thesis.md           ← one-page statement of the argument
    ├── audience_takeaways.md    ← what attendees leave with
    ├── objections_and_answers.md ← FAQ / counter-arguments
    └── demo_script.md           ← the on-stage choreography
```

---

## The thesis in one line

> Modern AI systems improve primarily through feedback orchestration, memory,
> evaluators, telemetry, and runtime adaptation — **not** through continuous
> retraining of model weights.

Or, more bluntly:

> Retrieval alone is not self-improvement. Behavioral adaptation is.

The talk argues the **model is increasingly becoming the least interesting
component**. This repo exists to make that claim runnable on your laptop in
under five minutes.

For the full argument see [`talk/core_thesis.md`](./talk/core_thesis.md) and
[`talk/audience_takeaways.md`](./talk/audience_takeaways.md). For pre-emptive
answers to the usual skeptics' questions ("isn't this just RAG?",
"isn't this just chat history?"), see
[`talk/objections_and_answers.md`](./talk/objections_and_answers.md).

---

## License

Treat as MIT — copy, fork, present, modify, share.
