/** StepWise API types (mirror the FastAPI schemas). */

export interface Impact {
  kg: number;
  co2e_kg: number;
  kwh: number;
  litres: number;
  kg_food: number;
  items: number;
}

export interface Reframe {
  statement: string;
  focus: string;
  lever: string;
  category: string;
  confidence: number;
}

export interface ActionDTO {
  action_id: string;
  title: string;
  category: string;
  impact: Impact;
  execution_unit: string;
  baseline_effort: number;
  cost_usd: number;
  duration_minutes: number;
  chosen_by: string;
  score: number | null;
  note: string | null;
  needs_learning: boolean;
}

export interface FeasibleGroup {
  name: string;
  actions: ActionDTO[];
  multiplier: number;
  total_effort_score: number;
  total_cost_usd: number;
  total_schedule_minutes: number;
  impact: Impact;
}

export interface MilestoneDTO {
  title: string;
  due_offset_days: number;
  done: boolean;
  note: string;
}

export interface Plan {
  reframe: Reframe;
  category: string;
  chosen: ActionDTO[];
  feasibility: FeasibleGroup[];
  milestones: MilestoneDTO[];
  total_impact: Impact;
  explanation: string;
}

export interface CheckIn {
  id: string;
  date: string;
  action_ids: string[];
  notes: string;
  feeling_score: number;
}

export interface Goal {
  id: string;
  goal_text: string;
  reframed_goal: string;
  category: string;
  scope: string;
  horizon_days: number;
  weekly_effort_hours: number;
  weekly_budget_usd: number;
  status: string;
  plan: Plan;
  impact: Impact;
  check_ins: CheckIn[];
  created_at: string;
}

export interface ChatResult {
  reply: string;
  provider: string;
  used_fallback: boolean;
  cached: boolean;
}

export interface NewGoalInput {
  goal_text: string;
  weekly_effort_hours: number;
  weekly_budget_usd: number;
  horizon_days: number;
}

export interface CheckInInput {
  action_ids: string[];
  notes?: string;
  feeling_score?: number;
  check_in_date?: string;
}
