# StepWise — NextStep Hacks 2026

> Turn environmental goals into measurable next steps.

**Event:** NextStep Hacks 2026 (HackAlphaX / Devpost) · **Theme:** Earth Forward
**Build window:** Aug 21 – Sep 13, 2026 · **Deadline:** Sep 13, 2026 @ 5:00pm EDT
**Event verified:** ✅ Yes (rules + overview fetched 2026-09-06)

## What it is

StepWise is an AI sustainability coach that turns a vague environmental worry
("I throw away too much plastic") into a **concrete, measurable action plan** —
and then tracks it.

The problem it attacks: most climate-concerned people never act because broad
goals don't produce behaviour. StepWise **reframes** the worry into a target
the person controls, **scores** candidate actions with a real decision model
(benefit vs. friction: effort, cost, time, habit, learning), works out what is
actually **feasible** given the person's time and budget, and then coaches them
day to day — with cumulative impact (waste kg, CO₂e, kWh, water litres, food kg,
items) and a consistency streak.

**Why it's interesting (and honest about it):** the recommendation logic is a
deterministic, unit-tested decision model — *not* the LLM's opinion. The model
is inspired by the behavioural-science concepts of *sludge* (friction that
blocks intended action) and the *intention–action gap*. The LLM layer makes the
same numbers conversational; with no API key configured the app runs fully on
deterministic local skills.

## Features

- **Reframe** — your concern becomes one specific behaviour target with a
  clearly named lever.
- **Decision-scored plan** — 28 curated actions across 6 categories (waste,
  energy, water, transport, food, consumption), each with quantified impact
  and friction attributes; scored and ranked deterministically.
- **Feasibility analysis** — how many times each action can realistically be
  done within your committed time and budget over the chosen horizon.
- **Milestones** — a schedule from "learn one fact" to the 30-day review.
- **Daily check-ins** — one-tap logging; impact meters update cumulatively,
  with a 7-day activity chart and streak.
- **AI coach** — chat that explains *why* an action was chosen (it cites the
  scoring model), unblocks you when stuck, and reviews progress. Falls back to
  deterministic local skills when no API key is set.
- **Auth & persistence** — email/password accounts (PBKDF2), opaque session
  tokens, per-user plans.

## Architecture

```
web/  React + TypeScript + Vite (typed API client, shared UI kit)
app/
  core/                 generic foundation (config, logging, errors, HTTP
                        factory, rate limiting, SQLAlchemy, auth, AI gateway)
  features/sustainability/
    core.py             decision model: ImpactVector, detriment/benefit
                        scoring, feasibility, streaks (pure, no deps)
    library.py          curated action catalogue (domain knowledge)
    engine.py           planner: reframe → score → feasible → milestones
    repository.py       persistence (goals, check-ins)
    service.py          orchestration (planner + AI gateway)
    routers.py          REST API
    ai_skills.py        deterministic AI skills + LLM prompt layer
```

The generic foundation is shared with the author's other hackathon repos;
**everything in `app/features/` is unique to this competition** and was built
during the Aug 21 – Sep 13, 2026 window (first commit in this repo: Sep 6,
2026 — see git log).

## Quick start

```bash
# backend (Python 3.11+)
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
# → API docs http://localhost:8000/api/docs
# → demo account: demo@example.com / demo-password-123

# web (separate terminal)
cd web
npm install
npm run dev        # http://localhost:5173 (proxies /api → :8000)

# tests
python -m pytest
```

## AI configuration

| Variable | Default | Notes |
|---|---|---|
| `AI_MODE` | `auto` | remote when a key is set, deterministic local otherwise |
| `AI_BASE_URL` | `https://api.openai.com/v1` | any OpenAI-compatible endpoint |
| `AI_API_KEY` | *(empty)* | empty → built-in deterministic demo skills |
| `AI_MODEL` | `gpt-4o-mini` | |

No API key is required to demo the full product. When a key is configured, the
same flows use the remote LLM with the engine's numbers still driving the UI.

## Honest notes (for judges & reviewers)

- **Impact estimates are order-of-magnitude**, typical-value figures chosen for
  teaching, not precision claims. The README + UI label them as estimates; the
  architecture makes it trivial to swap the `library.py` numbers for
  region-specific data (e.g. EPA/UK DEFRA factors).
- **No greenwashing**: StepWise measures *your* actions, in units you can
  actually verify (kWh on a bill, litres per minute, kg per bag), rather than
  projecting world-saving abstractions.
- **AI assistance disclosure:** development used AI coding tools (Claude-based
  agent tooling on the Arena.ai platform). Every change was reviewed by the
  author; the product's decision logic is deterministic and fully explained by
  the code + tests. See `docs/COMPLIANCE.md`.

## Deployment

`Dockerfile` + `docker compose up --build` serve the built frontend + API on
port 8000. CI (`backend: pytest`, `web: tsc + vite build`) runs on every push.

## License

MIT — see [LICENSE](LICENSE).
