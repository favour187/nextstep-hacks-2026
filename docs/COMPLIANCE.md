# Compliance & rules notes — StepWise (NextStep Hacks 2026)

*Repository created:* 2026-09-06 · All work committed on or after that date.

## Event facts (verified from official sources on 2026-09-06)

| Field | Value |
|---|---|
| Event | NextStep Hacks 2026 (HackAlphaX / Devpost) |
| Theme | **Earth Forward** (environmental challenges) |
| Build window | **Aug 21 – Sep 13, 2026** |
| Submission deadline | Sep 13, 2026 @ 5:00pm EDT (21:00 UTC) |
| Eligibility | anyone 13–24 as of Aug 21, 2026; teams ≤ 5 |
| Rules source | nextstep2026.devpost.com/rules + overview page |

## Originality / build-period compliance

- **Nothing pre-exists.** The repository was created on 2026-09-06 with no
  prior code; every commit is inside the Aug 21 – Sep 13 window (git log).
- **Not a continuation.** The rules require disclosure if an old project is
  continued; this is a brand-new project, so nothing needed disclosing — but
  the first commit date is stated in the README anyway.
- **Single use.** This project is submitted only to NextStep Hacks 2026. It is
  not submitted to any other hackathon, and its unique logic
  (`app/features/sustainability/`) is not reused elsewhere.
- **Shared foundation disclaimer.** `app/core/` is generic infrastructure
  (config, auth, DB, error handling, AI gateway) also present in the author's
  other hackathon repos. It contains no competition logic: the Earth Forward
  theme, the decision model and all product behaviour live in
  `app/features/sustainability/` which is unique to this repo.

## AI tool disclosure

The development of this project used AI coding assistance (Claude-based agent
tooling on the Arena.ai platform). This is disclosed openly, as the rules
permit and expect. Every AI-assisted change was reviewed and understood by the
author, who can explain any part of the codebase. The product's core decision
logic is deterministic, unit-tested code, not model output.

## Deliverables checklist (for submission day)

- [x] Public repository with runnable README
- [x] Working product with real data flows (verified end-to-end)
- [x] Backend tests green (14), frontend type-check + build green
- [ ] Demo video ≤ 5 minutes (recorder: author)
- [ ] Screenshots (≥ 1 UI) for the Devpost page
- [ ] Devpost page: description, Built With (incl. AI tool disclosure), team info
- [ ] Submission only after the above are complete and before Sep 13, 2026 5:00pm EDT

## Rule-specific design choices

- Adherence to track: the entire product is explicitly about environmental
  behaviour (theme judged).
- Originality: the reframe→score→feasibility→coach loop with a transparent
  decision model is the differentiator, not a generic to-do app.
- Completion: every feature in the README is implemented and tested.
- Design: mobile-first responsive UI, light/dark tokens, single-origin
  deployment.
- Technology: real decision-theoretic computation (benefit vs friction
  scoring), deterministic + LLM hybrid AI layer, 14 unit/API tests.
