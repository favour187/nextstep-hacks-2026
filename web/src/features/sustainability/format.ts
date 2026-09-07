import type { Impact } from "./types";
export const CATEGORY_LABEL: Record<string, string> = {
    waste: "Waste",
    energy: "Energy",
    water: "Water",
    transport: "Transport",
    food: "Food",
    consumption: "Consumption",
};
export const CATEGORY_TONE: Record<string, "accent" | "success" | "warning" | "danger" | "neutral"> = {
    waste: "neutral",
    energy: "warning",
    water: "accent",
    transport: "success",
    food: "success",
    consumption: "neutral",
};
export function fmtNum(value: number, digits = 1): string {
    const rounded = Math.round(value * 10 ** digits) / 10 ** digits;
    return rounded.toLocaleString(undefined, { maximumFractionDigits: digits });
}
export function fmtImpact(key: keyof Impact, value: number): string {
    const unit: Record<keyof Impact, string> = {
        kg: "kg waste",
        co2e_kg: "kg CO₂e",
        kwh: "kWh",
        litres: "L water",
        kg_food: "kg food",
        items: "items",
    };
    return `${fmtNum(value)} ${unit[key]}`;
}
export function effortLabel(score: number): string {
    if (score >= 0.78)
        return "Very easy";
    if (score >= 0.62)
        return "Easy";
    if (score >= 0.5)
        return "Moderate";
    return "Challenging";
}
export const IMPACT_ROWS: Array<{
    key: keyof Impact;
    label: string;
    icon: string;
}> = [
    { key: "kg", label: "Waste avoided", icon: "🗑️" },
    { key: "co2e_kg", label: "CO₂e avoided", icon: "🌍" },
    { key: "kwh", label: "Energy saved", icon: "⚡" },
    { key: "litres", label: "Water saved", icon: "💧" },
    { key: "kg_food", label: "Food saved", icon: "🥕" },
    { key: "items", label: "Items avoided", icon: "📦" },
];
export function weeklyActivity(checkIns: {
    date: string;
}[]): {
    label: string;
    count: number;
}[] {
    const days: {
        label: string;
        count: number;
    }[] = [];
    const now = new Date();
    for (let i = 6; i >= 0; i--) {
        const d = new Date(now);
        d.setDate(now.getDate() - i);
        const iso = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
        const count = checkIns.filter((c) => c.date.slice(0, 10) === iso).length;
        days.push({ label: d.toLocaleDateString(undefined, { weekday: "short" }), count });
    }
    return days;
}
export function streakDays(checkIns: {
    date: string;
}[]): number {
    const days = new Set(checkIns.map((c) => c.date.slice(0, 10)));
    let streak = 0;
    const cursor = new Date();
    const key = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    if (!days.has(key(cursor)))
        cursor.setDate(cursor.getDate() - 1);
    while (days.has(key(cursor))) {
        streak += 1;
        cursor.setDate(cursor.getDate() - 1);
    }
    return streak;
}
