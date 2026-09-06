/** StepWise dashboard: impact, next action, plan board, milestones, coach. */
import { useMemo, useState } from "react";
import { sustainabilityApi } from "./api";
import { AiCoach } from "./AiCoach";
import { BarChart, ImpactMeter } from "./Charts";
import {
  CATEGORY_LABEL,
  CATEGORY_TONE,
  IMPACT_ROWS,
  effortLabel,
  fmtImpact,
  fmtNum,
  streakDays,
  weeklyActivity,
} from "./format";
import { Badge, Button, Card, EmptyState, ErrorBanner, cx } from "../../ui/components";
import type { Goal } from "./types";

interface Props {
  goal: Goal;
  onRefresh: () => void;
  onNewPlan: () => void;
}

export function Dashboard({ goal, onRefresh, onNewPlan }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const plan = goal.plan;
  const top = plan.chosen[0] ?? null;
  const streak = streakDays(goal.check_ins);
  const activity = weeklyActivity(goal.check_ins);

  const topImpact = useMemo(() => {
    const max = plan.chosen.length
      ? plan.chosen[0].impact.kg + plan.chosen[0].impact.co2e_kg + 1e-9
      : 1;
    return max;
  }, [plan.chosen]);

  async function submitCheckIn() {
    if (selected.size === 0) return;
    setSaving(true);
    setError(null);
    try {
      await sustainabilityApi.checkIn(goal.id, { action_ids: [...selected] });
      setSelected(new Set());
      onRefresh();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <div className="page">
      {/* Header */}
      <div className="spread">
        <div>
          <div className="row" style={{ gap: 8, marginBottom: 6 }}>
            <Badge tone={CATEGORY_TONE[goal.category] ?? "accent"}>
              {CATEGORY_LABEL[goal.category] ?? goal.category}
            </Badge>
            <Badge tone={streak > 0 ? "success" : "neutral"}>🔥 {streak}-day streak</Badge>
            <Badge tone="neutral">{goal.horizon_days}-day plan</Badge>
          </div>
          <h1 style={{ margin: 0 }}>Your impact so far</h1>
          <p style={{ color: "var(--text-2)", margin: "8px 0 0" }}>{goal.goal_text}</p>
        </div>
        <Button variant="secondary" onClick={onNewPlan}>
          + New plan
        </Button>
      </div>

      {/* Reframe card */}
      <Card style={{ borderLeft: "4px solid var(--accent)" }}>
        <div className="row" style={{ gap: 8, marginBottom: 6 }}>
          <Badge tone="accent">reframed</Badge>
        </div>
        <p style={{ margin: 0, fontSize: 16 }}>{plan.reframe.statement}</p>
      </Card>

      {/* Impact + activity */}
      <div className="grid-2">
        <Card className="stack">
          <span className="spread">
            <h3 style={{ margin: 0 }}>Impact</h3>
            <Badge tone="success">cumulative</Badge>
          </span>
          {IMPACT_ROWS.filter((r) => goal.impact[r.key] > 0).length === 0 ? (
            <p style={{ color: "var(--text-2)", fontSize: 14, margin: 0 }}>
              No impact recorded yet. Check in below to start the counter.
            </p>
          ) : (
            IMPACT_ROWS.filter((r) => goal.impact[r.key] > 0).map((r) => (
              <ImpactMeter
                key={r.key}
                label={`${r.icon} ${r.label}`}
                value={goal.impact[r.key]}
                max={topImpact}
              />
            ))
          )}
        </Card>

        <Card>
          <span className="spread">
            <h3 style={{ margin: 0 }}>This week</h3>
            <Badge tone="neutral">{goal.check_ins.length} check-ins</Badge>
          </span>
          <BarChart data={activity} />
          <p style={{ fontSize: 12, color: "var(--text-3)", margin: "8px 0 0" }}>
            Days with at least one completed action. Consistency beats intensity.
          </p>
        </Card>
      </div>

      {/* Next action + plan board */}
      <div className="grid-2" style={{ gridTemplateColumns: "minmax(0, 1.1fr) minmax(0, 0.9fr)" }}>
        <Card className="stack">
          <span className="spread">
            <h3 style={{ margin: 0 }}>Next best action</h3>
            {top && <Badge tone="accent">{effortLabel(top.score ?? 0)}</Badge>}
          </span>
          {top ? (
            <>
              <p style={{ fontSize: 17, margin: 0, fontWeight: 600 }}>{top.title}</p>
              <p style={{ margin: 0, fontSize: 13, color: "var(--text-2)" }}>
                Benefit: {fmtImpact("kg", top.impact.kg)} · {fmtImpact("co2e_kg", top.impact.co2e_kg)} ·{" "}
                {fmtImpact("litres", top.impact.litres)} · {fmtImpact("kwh", top.impact.kwh)}
              </p>
              <div className="row" style={{ gap: 8 }}>
                <Badge tone="neutral">~{top.duration_minutes} min</Badge>
                <Badge tone="neutral">${fmtNum(top.cost_usd)}</Badge>
                <Badge tone={top.needs_learning ? "warning" : "success"}>
                  {top.needs_learning ? "needs a little learning" : "no research needed"}
                </Badge>
              </div>
              <p style={{ margin: 0, fontSize: 13, color: "var(--text-2)", fontStyle: "italic" }}>
                Why: the scoring model weighs benefit against friction — this action gives you the
                best effect per unit of effort, and it's the kind you can repeat tomorrow.
              </p>
            </>
          ) : (
            <EmptyState title="No actions yet" />
          )}
        </Card>

        <Card className="stack">
          <span className="spread">
            <h3 style={{ margin: 0 }}>What's achievable</h3>
            <Badge tone="neutral">{goal.horizon_days} days</Badge>
          </span>
          {plan.feasibility.map((group) => (
            <div key={group.name} className="stack" style={{ gap: 8 }}>
              <div className="spread">
                <strong style={{ fontSize: 14, textTransform: "capitalize" }}>{group.name}</strong>
                <Badge tone="success">×{group.multiplier} in the plan</Badge>
              </div>
              <p style={{ margin: 0, fontSize: 12, color: "var(--text-2)" }}>
                {group.actions.map((a) => a.title).join(" · ")} —{" "}
                {fmtImpact("kg", group.impact.kg)} / {fmtImpact("co2e_kg", group.impact.co2e_kg)} /
                {fmtImpact("litres", group.impact.litres)}
              </p>
            </div>
          ))}
        </Card>
      </div>

      {/* Plan board + milestones */}
      <div className="grid-2">
        <Card className="stack">
          <span className="spread">
            <h3 style={{ margin: 0 }}>Do today</h3>
            <Button
              size="sm"
              loading={saving}
              disabled={selected.size === 0}
              onClick={() => void submitCheckIn()}
            >
              Log {selected.size > 0 ? `${selected.size} done` : "check-in"}
            </Button>
          </span>
          <ErrorBanner message={error} />
          {plan.chosen.map((action) => {
            const checked = selected.has(action.action_id);
            return (
              <label
                key={action.action_id}
                className={cx("row", "checkin-row", checked && "checkin-row-done")}
                style={{
                  gap: 10,
                  padding: 10,
                  borderRadius: 10,
                  border: "1px solid var(--border)",
                  cursor: "pointer",
                  background: checked ? "var(--success-soft)" : "transparent",
                }}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggle(action.action_id)}
                  style={{ width: 18, height: 18, accentColor: "var(--accent)" }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{action.title}</div>
                  <div style={{ fontSize: 12, color: "var(--text-3)" }}>
                    {fmtImpact("kg", action.impact.kg)} · {fmtImpact("co2e_kg", action.impact.co2e_kg)} ·{" "}
                    {fmtImpact("litres", action.impact.litres)} · ~{action.duration_minutes} min
                  </div>
                </div>
                {action.score !== null && (
                  <Badge tone="neutral">{Math.round(action.score * 100)}% fit</Badge>
                )}
              </label>
            );
          })}
        </Card>

        <Card className="stack">
          <h3 style={{ margin: 0 }}>Milestones</h3>
          {plan.milestones.map((m, i) => (
            <div key={i} className="row" style={{ gap: 10, alignItems: "flex-start" }}>
              <span
                className={cx(
                  "milestone-dot",
                  m.done && "milestone-dot-done"
                )}
                style={{
                  width: 14,
                  height: 14,
                  borderRadius: "50%",
                  border: "2px solid var(--text-3)",
                  marginTop: 4,
                  flexShrink: 0,
                  background: m.done ? "var(--success)" : "transparent",
                }}
              />
              <div>
                <div style={{ fontSize: 14, fontWeight: m.done ? 600 : 400 }}>{m.title}</div>
                <div style={{ fontSize: 12, color: "var(--text-3)" }}>
                  day {m.due_offset_days} · {m.done ? "done" : "upcoming"}
                </div>
              </div>
            </div>
          ))}
        </Card>
      </div>

      {/* Coach */}
      <Card>
        <span className="spread">
          <h3 style={{ margin: 0 }}>AI coach</h3>
          <Badge tone="warning">explains decisions, always</Badge>
        </span>
        <AiCoach goalId={goal.id} />
      </Card>
    </div>
  );
}
