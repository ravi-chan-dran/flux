/**
 * TypeScript interfaces for FLUX frontend
 * Matching backend API types
 */

export interface ResearchRequest {
  question: string;
  max_iterations?: number;
  quality_threshold?: number;
  improvement_threshold?: number;
}

export interface ResearchResponse {
  research_id: string;
  question: string;
  status: string;
  message: string;
}

export interface AgentMessage {
  agent: string;
  emoji: string;
  color: string;
  role: string;
  message: string;
  message_type: string;
  timestamp: string;
  metadata?: {
    count?: number;
    hypotheses?: Hypothesis[];
    sources?: Source[];
    experiments?: Experiment[];
    synthesis?: any;
    quality_score?: number;
    issues?: string[];
    strengths?: string[];
    recommendations?: string[];
    [key: string]: any;
  };
}

export interface Hypothesis {
  id: string;
  text: string;
  confidence: number;
  reasoning: string;
  test_approach: string;
  iteration_generated?: number;
}

export interface Source {
  title: string;
  authors: string[];
  year: number | string;
  abstract: string;
  url: string;
  source_type: string;
  citation_count?: number;
  paper_id?: string;
}

export interface Experiment {
  hypothesis_id: string;
  method: string;
  measurements: string;
  success_criteria: string;
  time_estimate: string;
  potential_issues: string;
}

export interface Critique {
  quality_score: number;
  issues: string[];
  strengths: string[];
  recommendations: string[];
  raw_critique?: string;
}

export interface ResearchState {
  question: string;
  research_id: string;
  iteration: number;
  max_iterations: number;
  quality_score: number;
  quality_threshold: number;
  quality_history: number[];
  improvement_threshold: number;
  phase: string;
  next_action: string;
  should_iterate: boolean;
  stop_reason: string;
  hypotheses: Hypothesis[];
  sources: Source[];
  experiments: Experiment[];
  critiques: Critique[];
  paper_draft: string;
  messages: AgentMessage[];
  started_at: string;
  total_tokens_used: number;
  total_cost: number;
}

export interface Paper {
  research_id: string;
  paper: string;
  metadata: {
    question: string;
    started_at: string;
    completed_at: string;
    total_iterations: number;
    final_quality_score: number;
    quality_history: number[];
    stop_reason: string;
    total_tokens_used: number;
    total_cost: number;
  };
  conversation?: AgentMessage[];
  state?: ResearchState;
}

export interface PaperListItem {
  research_id: string;
  question: string;
  completed_at: string;
  final_quality_score: number;
  total_iterations: number;
  stop_reason: string;
}

export interface StreamEvent {
  research_id: string;
  node?: string;
  phase?: string;
  iteration?: number;
  quality_score?: number;
  next_action?: string;
  message?: string;
  agent?: string;
  emoji?: string;
  timestamp?: string;
  status?: string;
  error?: string;
}

// Agent color mapping
export const AGENT_COLORS = {
  "The Flow Master": "#9333EA", // purple
  "The Current": "#06B6D4", // cyan
  "The Source": "#F59E0B", // amber
  "The Channel": "#14B8A6", // teal
  "The Filter": "#EF4444", // red
  "The Confluence": "#6366F1", // indigo
} as const;

// Phase names
export const PHASES = [
  "Ideation",
  "Research",
  "Design",
  "Critique",
  "Synthesis",
] as const;

export type Phase = typeof PHASES[number];

// Agent info
export interface AgentInfo {
  name: string;
  emoji: string;
  color: string;
  role: string;
}

export const AGENTS: AgentInfo[] = [
  {
    name: "The Flow Master",
    emoji: "🧑‍💼",
    color: "#9333EA",
    role: "Orchestrator",
  },
  {
    name: "The Current",
    emoji: "💡",
    color: "#06B6D4",
    role: "Hypothesis Generator",
  },
  {
    name: "The Source",
    emoji: "📚",
    color: "#F59E0B",
    role: "Research Searcher",
  },
  {
    name: "The Channel",
    emoji: "🔬",
    color: "#14B8A6",
    role: "Experiment Designer",
  },
  {
    name: "The Filter",
    emoji: "🛡️",
    color: "#EF4444",
    role: "Quality Critic",
  },
  {
    name: "The Confluence",
    emoji: "✍️",
    color: "#6366F1",
    role: "Paper Synthesizer",
  },
];

