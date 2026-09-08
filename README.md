# StepWise

AI-assisted sustainability planning that turns an environmental goal into a measurable action plan.

## Features

- Goal reframing and action planning
- Deterministic impact and feasibility scoring
- Milestones and daily check-ins
- Progress, impact and streak tracking
- Optional AI coach
- User accounts and persistence

## Stack

- Python, FastAPI, SQLAlchemy
- React, TypeScript, Vite
- SQLite/PostgreSQL
- Docker

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd web
npm install
npm run dev
```

Run tests:

```bash
python -m pytest
```

## Environment

Optional AI configuration:

- `AI_MODE`
- `AI_BASE_URL`
- `AI_API_KEY`
- `AI_MODEL`

The app can run without an AI API key using its built-in deterministic skills.

## Demo

https://stepwise-8ev4.onrender.com

## License

MIT — see `LICENSE`.
