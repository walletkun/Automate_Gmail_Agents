# PROJECT.md

Living context for the email agent. Update at the end of each session.
Paste into a new chat to restore context in one message.

---

## Goal

Learn AI agents from first principles. The email agent is the vehicle, not
the point. Priority is understanding mechanics over shipping fast —
deliberately building things frameworks would give for free, so that when
a framework is adopted later it's a known quantity rather than a black box.

## What the thing does

Gmail → classify → research (branches by category) → markdown digest → inbox.
Learns preferences over time from replies, written to `prefs.json`.

---

## Decisions made

| Decision       | Choice                                                        | Why                                                              |
|----------------|---------------------------------------------------------------|------------------------------------------------------------------|
| Learning order | Raw API → tools → loop → memory → multi-agent → own framework | Frameworks make sense only after the thing they abstract         |
| Architecture   | 5 stages, Pydantic contracts between each                     | Contracts are the architecture; agents are swappable             |
| Control flow   | Deterministic Python routes, LLM only judges                  | Debuggable. LLM outputs a category; code decides what that means |
| Testing        | `.eml` fixtures, not live Gmail                               | Free, offline, instant iteration                                 |
| Gmail          | Added LAST (session 5)                                        | OAuth is the slowest loop; keep it out of the way                |
| Provider       | Behind `src/llm.py`, one file                                 | Swap models without touching anything else                       |
| Framework      | Plain Python first, LangGraph in session 4                    | Write the `if` before learning `add_conditional_edges`           |
| Hosting        | **Local only.** No cloud.                                     | Deploying solves "laptop closed" — not a problem we have         |
| Logging        | Every stage → `runs/{run_id}/`                                | Can't debug a pipeline you can't replay                          |
| Inference      | Hosted for now. Local (Ollama) benchmarked later              | Don't debug agent                                                |
mechanics and flaky local tool-calling simultaneously |
### Rejected, with reasons

- **CrewAI** — role/goal/backstory metaphor; branching per category is awkward.
Read its source after session 5 rather than building on it.
- **LangChain** — more abstraction than the skeleton, high API churn. LangGraph
is the part worth learning.
- **n8n** — workflow plumbing, not an agent framework. One workflow doesn't
justify it. Write the Gmail poller by hand instead.
- **OpenClaw** — read its markdown-memory and SKILL.md design after session 5.
Don't install as a starting point; it'd skip all the learning.

### Not in scope

Hosting, deployment, cloud of any kind. Runs on the laptop, invoked by hand.
Revisit only once sessions 1–5 are done and the thing works. Nothing in the
build plan requires a server, and adding one adds failure modes that make
agent bugs harder to diagnose.

---

## Build sessions

- [ ] **1 — ingest + classify.** `.eml` → `RawEmail` → `Classification`, printed.
Skeleton exists. TODOs: `extract_body()` (HTML-only emails return empty),
classification prompt (useful/skip boundary needs few-shot examples).
- [ ] **2 — agent loop + Tavily.** The while-loop from Level 2. Print the full
`messages` array every iteration. Break a tool on purpose and watch what
the model does.
- [ ] **3 — second agent.** Pass a string from research → prep. Branch on
category with a plain `if`. Add `asyncio.gather` for parallel research.
- [ ] **4 — synthesis + `prefs.json`.** Markdown digest. Then port the branching
to LangGraph and diff against the hand-written version.
- [ ] **5 — live Gmail.** OAuth, `historyId`, processed-ID table. The only
session that fights Google.

---

## Open questions

- Which model per stage? Classification is high-volume/easy (cheap model),
synthesis determines whether output is worth reading (stronger model).
- Gemini free tier: generous, but free-tier inputs may be used for training —
and this pipeline reads personal email. Vertex AI avoids that. Undecided.
- Rate limits vs. parallel agents: 3 agents × ~5 loop iterations = a burst that
will trip free-tier RPM. Needs backoff + a concurrency cap either way.
- Local vs hosted: deferred. Once fixtures pass on hosted, point ONLY the
classifier at Ollama and diff against saved runs/. Classification should
hold up on a small model; synthesis and tool-calling are where they fall down.
- Quoted reply chains inflate body size (2.4k vs 18k chars across two messages
in the same thread). Not stripping for now — the quoted text carries real
history (relocation, availability, round structure). Revisit only if it
causes classification errors or token pressure.

## Known traps

- Gmail OAuth: External + Testing status expires refresh tokens after 7 days.
(Session 5 only. Not an issue while running by hand.)
- Enabling billing on a Google project deletes that project's free tier.
- Agent loops need a max-turns cap and a cost ceiling. Non-negotiable.
- Human gate on sending email until output is trusted — write to file first.

---

## Session log

**2026-07-26** — Architecture + curriculum settled. Skeleton scaffolded
(contracts, llm, ingest, classify, main). Nothing run yet.
Next: download fixtures, get session 1 printing a `Classification`.
