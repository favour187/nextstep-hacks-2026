/** StepWise AI coach: a chat that explains decisions and unblocks users. */
import { useRef, useState } from "react";
import { sustainabilityApi } from "./api";
import { Badge, Button, ErrorBanner, Spinner, cx } from "../../ui/components";

interface Message {
  role: "user" | "assistant";
  text: string;
  fallback?: boolean;
}

const SUGGESTIONS = [
  "Explain why this is my next step",
  "I'm stuck — what should I do today?",
  "Give me one tip to keep going",
  "Review my progress",
];

export function AiCoach({ goalId }: { goalId: string | null }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || busy) return;
    setError(null);
    setMessages((m) => [...m, { role: "user", text: trimmed }]);
    setInput("");
    setBusy(true);
    try {
      const res = await sustainabilityApi.chat(trimmed, goalId ?? undefined);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: res.reply, fallback: res.used_fallback },
      ]);
      requestAnimationFrame(() => listRef.current?.scrollTo({ top: 99999, behavior: "smooth" }));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="stack" style={{ minHeight: 320, display: "flex", flexDirection: "column" }}>
      <div
        ref={listRef}
        style={{
          flex: 1,
          overflowY: "auto",
          display: "grid",
          gap: 10,
          alignContent: "start",
          paddingRight: 4,
          minHeight: 220,
          maxHeight: 360,
        }}
      >
        {messages.length === 0 && (
          <div className="empty-state" style={{ padding: "var(--space-5)" }}>
            <h3 style={{ marginBottom: 8 }}>Ask the coach anything</h3>
            <p style={{ margin: 0, fontSize: 13 }}>
              StepWise explains every decision with its actual scoring model — ask why an action was
              chosen, or tell it you're stuck.
            </p>
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={cx("msg", m.role === "user" ? "msg-user" : "msg-assistant")}
            style={{
              maxWidth: "85%",
              padding: "10px 14px",
              borderRadius: 14,
              fontSize: 14,
              whiteSpace: "pre-wrap",
              background: m.role === "user" ? "var(--accent)" : "var(--surface-2)",
              color: m.role === "user" ? "#fff" : "var(--text)",
              justifySelf: m.role === "user" ? "end" : "start",
            }}
          >
            {m.text}
            {m.fallback && (
              <div style={{ marginTop: 6, fontSize: 11, opacity: 0.65 }}>
                <Badge tone="neutral">deterministic demo answer</Badge>
              </div>
            )}
          </div>
        ))}
        {busy && (
          <div style={{ justifySelf: "start" }}>
            <Spinner size={16} />
          </div>
        )}
      </div>

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            className="btn btn-secondary btn-sm"
            onClick={() => void send(s)}
            disabled={busy}
          >
            {s}
          </button>
        ))}
      </div>

      <ErrorBanner message={error} />
      <form
        className="row"
        style={{ alignItems: "stretch" }}
        onSubmit={(e) => {
          e.preventDefault();
          void send(input);
        }}
      >
        <input
          className="input"
          style={{ flex: 1 }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your plan…"
          aria-label="Chat message"
        />
        <Button type="submit" loading={busy}>
          Send
        </Button>
      </form>
    </div>
  );
}
