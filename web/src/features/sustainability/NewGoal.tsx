/** Create a new StepWise plan: describe the goal, set constraints, get the plan. */
import { useState } from "react";
import { sustainabilityApi } from "./api";
import { Button, Card, ErrorBanner, Input } from "../../ui/components";

const EXAMPLES = [
  "I want to reduce the plastic waste my household produces",
  "Lower my energy bill and my footprint",
  "Save more water at home",
  "Stop wasting food at home",
  "Drive less and walk more",
  "Buy fewer things I don't need",
];

export function NewGoal({ onCreated, onCancel }: { onCreated: () => void; onCancel: () => void }) {
  const [goalText, setGoalText] = useState("");
  const [hours, setHours] = useState(2);
  const [budget, setBudget] = useState(10);
  const [horizon, setHorizon] = useState(30);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (goalText.trim().length < 4) {
      setError("Describe your goal in at least a few words.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await sustainabilityApi.createGoal({
        goal_text: goalText.trim(),
        weekly_effort_hours: hours,
        weekly_budget_usd: budget,
        horizon_days: horizon,
      });
      onCreated();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <div className="spread">
        <div>
          <h1>Start a plan</h1>
          <p style={{ color: "var(--text-2)", margin: 0 }}>
            Tell StepWise what's on your mind — it will reframe it into a measurable plan.
          </p>
        </div>
        <Button variant="secondary" onClick={onCancel}>
          Back
        </Button>
      </div>

      <Card className="stack">
        <label className="field-label" htmlFor="goal">
          What do you want to change?
        </label>
        <Input
          id="goal"
          value={goalText}
          onChange={(e) => setGoalText(e.target.value)}
          placeholder="e.g. I want to reduce the waste my household produces"
          maxLength={400}
        />
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => setGoalText(ex)}
            >
              {ex.length > 46 ? `${ex.slice(0, 46)}…` : ex}
            </button>
          ))}
        </div>

        <div className="grid-2">
          <div className="field">
            <label className="field-label" htmlFor="hours">
              Time you can give: <strong>{hours} h/week</strong>
            </label>
            <input
              id="hours"
              type="range"
              min={0.5}
              max={10}
              step={0.5}
              value={hours}
              onChange={(e) => setHours(Number(e.target.value))}
            />
          </div>
          <div className="field">
            <label className="field-label" htmlFor="budget">
              Budget you can spend: <strong>${budget}/week</strong>
            </label>
            <input
              id="budget"
              type="range"
              min={0}
              max={50}
              step={5}
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
            />
          </div>
        </div>
        <div className="field">
          <label className="field-label" htmlFor="horizon">
            Commitment: <strong>{horizon} days</strong>
          </label>
          <input
            id="horizon"
            type="range"
            min={7}
            max={60}
            step={1}
            value={horizon}
            onChange={(e) => setHorizon(Number(e.target.value))}
          />
        </div>

        <ErrorBanner message={error} />
        <div>
          <Button size="lg" loading={busy} onClick={() => void submit()}>
            {busy ? "Building your plan…" : "Build my plan"}
          </Button>
        </div>
      </Card>

      <Card>
        <h3 style={{ marginTop: 0 }}>How the planner works</h3>
        <div className="grid-2">
          {[
            ["🔍", "Reframe", "Your broad concern becomes one specific, measurable behaviour target."],
            ["⚖️", "Score", "Every candidate action is scored on benefit vs. friction (effort, cost, time, habit, learning)."],
            ["📅", "Feasibility", "Your time and budget decide how often each action can realistically happen."],
            ["📈", "Track", "Check in daily; watch waste, CO₂e, kWh, water and items add up."],
          ].map(([icon, title, body]) => (
            <div key={title} className="row" style={{ alignItems: "flex-start" }}>
              <span style={{ fontSize: 24 }}>{icon}</span>
              <div>
                <strong>{title}</strong>
                <p style={{ margin: 0, fontSize: 13, color: "var(--text-2)" }}>{body}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
