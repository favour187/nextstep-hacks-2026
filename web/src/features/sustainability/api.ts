import { api } from "../../lib/api";
import type { ChatResult, CheckInInput, Goal, NewGoalInput } from "./types";
export const sustainabilityApi = {
    goals: () => api<{
        goals: Goal[];
    }>("/sustainability/goals"),
    goal: (id: string) => api<Goal>(`/sustainability/goals/${id}`),
    createGoal: (input: NewGoalInput) => api<Goal>("/sustainability/goals", { method: "POST", body: input }),
    checkIn: (goalId: string, input: CheckInInput) => api<{
        check_in: unknown;
        impact: Record<string, number>;
        streak: number;
    }>(`/sustainability/goals/${goalId}/check-ins`, { method: "POST", body: input }),
    chat: (message: string, goalId?: string) => api<ChatResult>("/sustainability/chat", {
        method: "POST",
        body: { message, goal_id: goalId ?? null },
    }),
};
