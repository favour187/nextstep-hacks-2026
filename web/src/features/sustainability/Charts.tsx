/** Tiny SVG charts (no external library). */
import { fmtNum } from "./format";

export function BarChart({
  data,
  height = 96,
}: {
  data: { label: string; count: number }[];
  height?: number;
}) {
  const max = Math.max(1, ...data.map((d) => d.count));
  return (
    <div style={{ display: "grid", gap: 6 }}>
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: 8,
          height,
        }}
      >
        {data.map((d, i) => {
          const h = Math.round((d.count / max) * (height - 12)) + 3;
          return (
            <div key={i} style={{ flex: 1, display: "grid", gap: 4, justifyItems: "center" }}>
              <div
                title={`${d.count} check-in${d.count === 1 ? "" : "s"}`}
                style={{
                  width: "70%",
                  height: h,
                  borderRadius: "6px 6px 0 0",
                  background: d.count > 0 ? "var(--accent)" : "var(--surface-2)",
                  transition: "height 0.3s",
                }}
              />
            </div>
          );
        })}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        {data.map((d, i) => (
          <div key={i} style={{ flex: 1, textAlign: "center", fontSize: 10, color: "var(--text-3)" }}>
            {d.label}
          </div>
        ))}
      </div>
    </div>
  );
}

export function ImpactMeter({ value, max, label }: { value: number; max: number; label: string }) {
  const pct = Math.min(100, Math.round((value / Math.max(1e-9, max)) * 100));
  return (
    <div style={{ display: "grid", gap: 4 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--text-2)" }}>
        <span>{label}</span>
        <span style={{ fontWeight: 700, color: "var(--text)" }}>{fmtNum(value)}</span>
      </div>
      <div style={{ height: 8, borderRadius: 999, background: "var(--surface-2)", overflow: "hidden" }}>
        <div
          style={{
            height: "100%",
            width: `${pct}%`,
            borderRadius: 999,
            background: "linear-gradient(90deg, var(--accent), var(--success))",
            transition: "width 0.5s ease",
          }}
        />
      </div>
    </div>
  );
}
