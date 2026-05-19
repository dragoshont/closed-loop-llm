# Agenda — 30-minute slot

Total slot: **30 minutes** = 25 min talk + 5 min Q&A.

## Time budget

| # | Section | Minutes | Notes |
|---|---|---|---|
| 1 | Intro (incl. compressed evolution-of-AI beat) | 3 | One opening line memorized verbatim. |
| 2 | Defining self-improving systems | 4 | The loop diagram. Act → evaluate → persist → adapt. |
| 3 | Retrieval vs behavioral adaptation | 3 | Central dichotomy. Do NOT drop below 3 min. |
| 4 | `karpathy/autoresearch` — canonical example | 3 | The 4-file frame; one anchor line. |
| 5 | Live demo (architecture + walkthrough merged) | 7 | The hero moment. Show 4-file structure on screen while loop runs. |
| 6 | Failure modes | 2 | Terse list, not a slide per item. Credibility multiplier. |
| 7 | Closing (incl. compressed "where leverage is now") | 3 | The memorable lines land here. Last sentence written down. |
|   | **Talk total** | **25** | |
|   | Q&A buffer | 5 | |
|   | **Grand total** | **30** | |

## What's load-bearing (do not cut)

- **Retrieval vs adaptation.** The talk's central dichotomy. Section 3.
- **The live demo.** The only thing the audience remembers in detail. Section 5.
- **Failure modes.** Single biggest credibility move (feedback poisoning, memory
  drift, evaluator failure, echo chambers). Section 6.

## What got merged or cut from the original 38-min plan

- "Evolution of AI systems" as a standalone section → compressed into the
  intro (section 1) as a 60-second beat.
- "Demo architecture" as a standalone slide → folded into the live demo
  (section 5). The 4-file diagram appears on screen *while* the loop runs.
- "Where the leverage is now" as a standalone section → folded into the
  closing (section 7).

## Memorable lines — placement

| Line | Where it lands |
|---|---|
| "The model is increasingly becoming the least interesting component." | Section 2, after the loop diagram. |
| "Retrieval alone is not self-improvement. Behavioral adaptation is." | Section 3, as the section's title/punchline. |
| "The human edits `program.md`. The agent edits `train.py`. Neither edits the model." | Section 4, on the autoresearch slide. |
| "Self-improvement without guardrails becomes self-degradation." | Section 6, opening of failure modes. |
| "Most production AI systems improve at the orchestration layer." | Section 7, closing. |

## Discipline

- **Opening 90 seconds:** write verbatim, memorize. No improvisation on the cold start.
- **Closing 60 seconds:** write verbatim, memorize. The last line is what they quote.
- **Demo:** pre-warm the model and the memory state before walking on stage. Run
  one `ask` to load model weights into cache so the first on-stage call is fast.
- **Q&A:** the four pre-answered objections live in
  [`objections_and_answers.md`](./objections_and_answers.md). Have a graceful
  "I don't know but here's how I'd find out" line ready for the one question
  you can't answer.

## What this demo proves on stage (and what it doesn't)

The live demo shows **behavioral adaptation**, not measurable improvement.
The honest framing — *"this is the substrate; `autoresearch` is the
goal-aligned layer on top"* — is itself a credibility move. Do not overclaim
the demo into "self-improvement"; the audience can smell it.

See the [root README's "What this demo shows" section](../README.md#what-this-demo-shows-and-what-it-deliberately-doesnt)
for the full framing.
