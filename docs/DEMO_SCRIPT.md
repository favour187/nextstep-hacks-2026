# StepWise — demo video script (target 3:30–4:30; rules require 3–5 minutes)

**Setup before recording**

```bash
rm -f data/app.db                               # fresh database
uvicorn app.main:app --reload --port 8000       # terminal 1
cd web && npm run dev                           # terminal 2 → http://localhost:5173
```

Register a fresh account (e.g. "Amina") rather than the demo account so the empty state shows. Record at 1280×800 or larger, 100 % zoom, light mode. Keep the terminal with `python -m pytest` output ready for the last beat.

| Time | On screen | Say |
|---|---|---|
| 0:00 | Landing page (logged out) | "Most people who care about the environment never change a habit — not because they don't care, but because 'reduce my footprint' is not an action. StepWise is a sustainability coach that turns a vague worry into a measurable plan, and then tracks it. It was built for NextStep Hacks' Earth Forward theme." |
| 0:25 | Create account → **Start a plan** | "Amina types what's bothering her." Click the example chip *"I want to reduce the plastic waste my household produces"*. "She tells it what she can realistically give: two hours and ten dollars a week, for 30 days." (Set sliders: 2 h, $10, 30 days.) |
| 0:50 | Click **Build my plan** → plan appears | "This is the interesting part. StepWise *reframes* the worry into one behaviour target with a named lever, then scores 28 curated actions with a real decision model — impact against friction: effort, cost, time, habit change, learning curve. The ranking is deterministic and unit-tested, not an LLM's opinion." |
| 1:20 | Dashboard → **Next best action** card | "The top action is explained: what it saves per week, in units you can verify on a bill or a bin — kilograms of waste, kWh, litres — and why it beat the alternatives." |
| 1:40 | **What's achievable** card | "Feasibility: given two hours and ten dollars a week, here's how many times each action can actually happen over 30 days. No plan that assumes infinite time." |
| 2:00 | **Milestones** | "A schedule from 'learn one fact today' to the 30-day review." |
| 2:10 | **Do today** → tick two actions → **Check in** → impact meters + chart update | "Daily check-ins are one tap. Impact accumulates — waste, CO₂e, energy, water, food, items — with a seven-day chart and a streak." |
| 2:40 | **AI coach** → click *"Explain why this is my next step"* | "The coach is grounded in the same numbers: it cites the scoring model, not vibes. Offline it runs on deterministic skills; with an API key the same prompt drives an LLM." Then *"I'm stuck — what should I do today?"* |
| 3:10 | Editor: `app/features/sustainability/` tree, `library.py` impact factors | "Architecture: FastAPI + SQLAlchemy backend, React/TypeScript front end. Every impact number lives in one data file with its unit and source note, labelled as order-of-magnitude teaching estimates — no greenwashing, no world-saving abstractions." |
| 3:35 | Terminal: `python -m pytest` → 14 passed; CI badge | "Fourteen tests cover the decision model, feasibility maths and the API; CI runs them plus the TypeScript build on every push. Docker Compose deploys it as a single origin." |
| 3:55 | Landing / end card with repo URL | "StepWise: a small, honest step, measured. Thank you." |

## Shot list for the Devpost page (capture while recording)

1. Landing page (hero)
2. Start-a-plan form with sliders
3. Dashboard: Next best action + What's achievable
4. Check-in with impact meters and 7-day chart
5. AI coach explaining the choice
6. Mobile width (≈ 390 px) dashboard

## Devpost copy blocks

**Tagline:** Turn environmental goals into measurable next steps.

**Built with:** Python 3.11, FastAPI, Pydantic, SQLAlchemy 2, SQLite, pytest, React 18, TypeScript, Vite, Docker, GitHub Actions. AI coding assistance (Claude-based agent tooling on Arena.ai) — disclosed.

**Description:** paste "What it is", "Features" and "Honest notes" from the README.
