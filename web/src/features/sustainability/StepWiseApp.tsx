/** StepWise root: landing → auth → dashboard / new plan. */
import { useEffect, useState } from "react";
import { sustainabilityApi } from "./api";
import { Dashboard } from "./Dashboard";
import { NewGoal } from "./NewGoal";
import { useAuth } from "../../lib/auth";
import { Badge, Button, Card, ErrorBanner, Input, Spinner } from "../../ui/components";
import type { Goal } from "./types";

type View = "landing" | "dashboard" | "new";

export function StepWiseApp() {
  const auth = useAuth();
  const [view, setView] = useState<View>("landing");
  const [goals, setGoals] = useState<Goal[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const active = goals.find((g) => g.id === activeId) ?? goals[0] ?? null;

  async function load() {
    if (!auth.user) return;
    setLoading(true);
    setError(null);
    try {
      const res = await sustainabilityApi.goals();
      setGoals(res.goals);
      setView(res.goals.length ? "dashboard" : "new");
      if (res.goals.length) setActiveId(res.goals[0].id);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!auth.user) {
      setView("landing");
      return;
    }
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auth.user]);

  if (!auth.user) {
    return <Landing />;
  }

  if (auth.booting || loading) {
    return (
      <div className="page" style={{ display: "grid", placeItems: "center", minHeight: "50vh" }}>
        <Spinner size={28} />
      </div>
    );
  }

  if (view === "new" || !active) {
    return <NewGoal onCreated={() => void load()} onCancel={() => setView(active ? "dashboard" : "new")} />;
  }

  return (
    <div>
      {goals.length > 1 && (
        <div className="row" style={{ gap: 8, paddingTop: 12 }}>
          <span style={{ fontSize: 13, color: "var(--text-2)" }}>Plans:</span>
          {goals.map((g) => (
            <button
              key={g.id}
              className={cx("btn", g.id === active.id ? "btn-primary" : "btn-secondary", "btn-sm")}
              onClick={() => setActiveId(g.id)}
            >
              {g.category}
            </button>
          ))}
        </div>
      )}
      <ErrorBanner message={error} />
      <Dashboard goal={active} onRefresh={() => void load()} onNewPlan={() => setView("new")} />
    </div>
  );
}

function cx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

function Landing() {
  const auth = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit() {
    if (!email || !password || (mode === "register" && !name)) {
      setError("Fill in all fields.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      if (mode === "login") await auth.login(email, password);
      else await auth.register(email, password, name);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <section
        style={{
          textAlign: "center",
          padding: "var(--space-8) var(--space-4)",
          display: "grid",
          gap: 16,
          justifyItems: "center",
        }}
      >
        <Badge tone="success">🌱 Earth Forward · NextStep Hacks 2026</Badge>
        <h1 style={{ fontSize: "clamp(30px, 6vw, 52px)", maxWidth: 760, margin: 0 }}>
          Small steps. <span style={{ color: "var(--accent)" }}>Measured</span> impact.
        </h1>
        <p style={{ maxWidth: 620, color: "var(--text-2)", fontSize: 17, margin: 0 }}>
          StepWise turns a vague environmental worry into a concrete action plan — scored by a
          decision model, not vibes — and shows your waste, water, energy and CO₂e adding up.
        </p>
      </section>

      <div className="grid-2" style={{ maxWidth: 900, margin: "0 auto" }}>
        {[
          ["🗣️", "Say the worry", "\u201CI throw away too much plastic.\u201D StepWise reframes it into a target you control."],
          ["🧭", "Get your plan", "A measured set of actions, ranked by benefit vs. friction, with milestones on the calendar."],
          ["✅", "Check in & grow", "Log what you did. Watch waste, CO₂e, kWh, water and items accumulate — and keep the streak."],
        ].map(([icon, title, body], i) => (
          <Card key={title} style={{ textAlign: "left" }}>
            <div style={{ fontSize: 28 }}>{icon}</div>
            <h3 style={{ margin: "10px 0 6px" }}>
              {i + 1}. {title}
            </h3>
            <p style={{ margin: 0, fontSize: 14, color: "var(--text-2)" }}>{body}</p>
          </Card>
        ))}
      </div>

      <div style={{ maxWidth: 460, margin: "var(--space-7) auto 0" }}>
        <Card className="stack">
          <span className="spread">
            <h3 style={{ margin: 0 }}>{mode === "login" ? "Welcome back" : "Create an account"}</h3>
            <Badge tone="neutral">demo-friendly</Badge>
          </span>
          <ErrorBanner message={error} />
          {mode === "register" && (
            <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />
          )}
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button size="lg" loading={busy} onClick={() => void submit()}>
            {mode === "login" ? "Log in" : "Create account"}
          </Button>
          <button
            className="btn btn-ghost"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            style={{ width: "100%" }}
          >
            {mode === "login" ? "New here? Create an account" : "Have an account? Log in"}
          </button>
          {mode === "login" && (
            <p style={{ fontSize: 12, color: "var(--text-3)", margin: 0, textAlign: "center" }}>
              Demo account: demo@example.com · demo-password-123
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
