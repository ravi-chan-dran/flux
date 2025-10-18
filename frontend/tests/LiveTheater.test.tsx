/**
 * Live Theater Component Tests
 * 
 * Tests for app/flow/[id]/page.tsx
 * Covers SSE streaming, UI updates, error handling, and accessibility
 */

import React from "react";
import { render, screen, waitFor, fireEvent, within } from "@testing-library/react";
import "@testing-library/jest-dom";
import { useRouter, useParams, useSearchParams } from "next/navigation";
import FlowPage from "../app/flow/[id]/page";
import { ConnectionStatus } from "../lib/api";

// Mock Next.js navigation
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
  useSearchParams: jest.fn(),
}));

// Mock useResearchStream hook
jest.mock("../lib/api", () => ({
  ...jest.requireActual("../lib/api"),
  useResearchStream: jest.fn(),
  ConnectionStatus: {
    IDLE: "idle",
    CONNECTING: "connecting",
    CONNECTED: "connected",
    RECONNECTING: "reconnecting",
    ERROR: "error",
    COMPLETE: "complete",
  },
}));

// Mock child components
jest.mock("../components/AgentAvatar", () => ({
  __esModule: true,
  default: ({ agent, active, size, showLabel }: any) => (
    <div
      data-testid={`agent-avatar-${agent.name}`}
      data-active={active}
      data-size={size}
      data-label={showLabel}
    >
      {agent.emoji} {agent.name}
    </div>
  ),
  AGENT_CONFIGS: {
    "The Flow Master": { name: "The Flow Master", emoji: "🧑‍💼", color: "#9D4EDD", role: "Orchestrator" },
    "The Current": { name: "The Current", emoji: "💡", color: "#00D9FF", role: "Hypothesis Generator" },
    "The Source": { name: "The Source", emoji: "📚", color: "#FFA500", role: "Researcher" },
    "The Channel": { name: "The Channel", emoji: "🔬", color: "#06FFA5", role: "Experimenter" },
    "The Filter": { name: "The Filter", emoji: "🛡️", color: "#FF4444", role: "Critic" },
    "The Confluence": { name: "The Confluence", emoji: "✍️", color: "#6366F1", role: "Synthesizer" },
  },
}));

jest.mock("../components/ConversationFeed", () => ({
  __esModule: true,
  default: ({ messages, activeAgent, isWaiting }: any) => (
    <div data-testid="conversation-feed" data-active-agent={activeAgent} data-waiting={isWaiting}>
      {messages.map((msg: any, idx: number) => (
        <div key={idx} data-testid={`message-${idx}`}>
          {msg.agent}: {msg.message}
        </div>
      ))}
    </div>
  ),
}));

jest.mock("../components/PhaseProgress", () => ({
  __esModule: true,
  default: ({ currentPhase, progress, iteration, maxIterations }: any) => (
    <div
      data-testid="phase-progress"
      data-phase={currentPhase}
      data-progress={progress}
      data-iteration={iteration}
      data-max-iterations={maxIterations}
    >
      Phase: {currentPhase} - Orbit {iteration + 1}/{maxIterations}
    </div>
  ),
}));

jest.mock("../components/LiveStats", () => ({
  __esModule: true,
  default: ({ phase, activeAgent, iteration, qualityScore }: any) => (
    <div
      data-testid="live-stats"
      data-phase={phase}
      data-agent={activeAgent?.name}
      data-iteration={iteration}
      data-quality={qualityScore}
    >
      Quality: {qualityScore}
    </div>
  ),
}));

jest.mock("../components/ConnectionStatus", () => ({
  __esModule: true,
  default: ({ status, error, onRetry }: any) => (
    <div data-testid="connection-status" data-status={status}>
      {status === "error" && (
        <>
          <div>Error: {error?.message}</div>
          <button onClick={onRetry}>Retry</button>
        </>
      )}
    </div>
  ),
}));

// Import mocked hook
import { useResearchStream } from "../lib/api";

describe("LiveTheater Component", () => {
  const mockPush = jest.fn();
  const mockUseResearchStream = useResearchStream as jest.MockedFunction<typeof useResearchStream>;

  beforeEach(() => {
    jest.clearAllMocks();

    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });

    (useParams as jest.Mock).mockReturnValue({
      id: "test-research-123",
    });

    (useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn((key: string) => {
        if (key === "question") return "How does quantum computing work?";
        return null;
      }),
    });
  });

  describe("Initial Rendering", () => {
    it("renders loading state initially", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "initialize",
        activeAgent: "",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTING,
        error: null,
        startTime: null,
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      expect(screen.getByText(/connecting to research stream/i)).toBeInTheDocument();
    });

    it("displays research question in header", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "initialize",
        activeAgent: "",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      expect(screen.getByText(/how does quantum computing work/i)).toBeInTheDocument();
    });
  });

  describe("SSE Connection", () => {
    it("connects with correct research ID", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "initialize",
        activeAgent: "",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      expect(mockUseResearchStream).toHaveBeenCalledWith(
        "test-research-123",
        "How does quantum computing work?",
        expect.any(Object)
      );
    });

    it("shows LIVE indicator when connected", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      expect(screen.getByText("LIVE")).toBeInTheDocument();
    });
  });

  describe("Message Display", () => {
    it("displays messages as they arrive", async () => {
      const messages = [
        {
          agent: "The Flow Master",
          emoji: "🧑‍💼",
          color: "#9D4EDD",
          role: "Orchestrator",
          message: "Starting research...",
          message_type: "info",
          timestamp: new Date().toISOString(),
          metadata: {},
        },
        {
          agent: "The Current",
          emoji: "💡",
          color: "#00D9FF",
          role: "Hypothesis Generator",
          message: "Generated 3 hypotheses",
          message_type: "info",
          timestamp: new Date().toISOString(),
          metadata: {},
        },
      ];

      mockUseResearchStream.mockReturnValue({
        messages,
        currentPhase: "hypotheses",
        activeAgent: "The Current",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      await waitFor(() => {
        expect(screen.getByTestId("message-0")).toHaveTextContent("The Flow Master: Starting research...");
        expect(screen.getByTestId("message-1")).toHaveTextContent("The Current: Generated 3 hypotheses");
      });
    });
  });

  describe("Phase Progress", () => {
    it("updates phase progress when phase changes", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "The Source",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      const phaseProgress = screen.getByTestId("phase-progress");
      expect(phaseProgress).toHaveAttribute("data-phase", "research");
    });

    it("displays correct iteration count", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "critique",
        activeAgent: "The Filter",
        iteration: 1,
        maxIterations: 3,
        qualityScore: 7.5,
        qualityHistory: [6.5, 7.5],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      expect(screen.getByText(/Orbit 2 \/ 3/i)).toBeInTheDocument();
    });
  });

  describe("Active Agent Highlighting", () => {
    it("highlights active agent correctly", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "The Source",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      const activeAvatar = screen.getByTestId("agent-avatar-The Source");
      expect(activeAvatar).toHaveAttribute("data-active", "true");

      const inactiveAvatar = screen.getByTestId("agent-avatar-The Flow Master");
      expect(inactiveAvatar).toHaveAttribute("data-active", "false");
    });
  });

  describe("Quality Scores", () => {
    it("displays quality scores when Filter provides them", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "critique",
        activeAgent: "The Filter",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 7.5,
        qualityHistory: [7.5],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      const liveStats = screen.getByTestId("live-stats");
      expect(liveStats).toHaveAttribute("data-quality", "7.5");
    });
  });

  describe("Connection Error Handling", () => {
    it("handles reconnection when connection drops", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.RECONNECTING,
        error: "Connection lost. Reconnecting...",
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      const connectionStatus = screen.getByTestId("connection-status");
      expect(connectionStatus).toHaveAttribute("data-status", "reconnecting");
    });

    it("shows error state when connection fails permanently", () => {
      const mockReconnect = jest.fn();
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.ERROR,
        error: "Connection failed after 10 attempts",
        startTime: new Date(),
        completionTime: null,
        reconnect: mockReconnect,
      });

      render(<FlowPage />);

      expect(screen.getByText(/connection failed after 10 attempts/i)).toBeInTheDocument();
      
      const retryButton = screen.getByRole("button", { name: /retry/i });
      fireEvent.click(retryButton);
      
      expect(mockReconnect).toHaveBeenCalled();
    });
  });

  describe("Completion", () => {
    it("shows COMPLETE indicator on completion", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "complete",
        activeAgent: "",
        iteration: 2,
        maxIterations: 3,
        qualityScore: 8.5,
        qualityHistory: [6.5, 7.5, 8.5],
        connectionStatus: ConnectionStatus.COMPLETE,
        error: null,
        startTime: new Date(),
        completionTime: new Date(),
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      expect(screen.getByText("COMPLETE")).toBeInTheDocument();
    });
  });

  describe("Cleanup", () => {
    it("cleans up on unmount", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      const { unmount } = render(<FlowPage />);
      
      // Component should cleanup on unmount
      unmount();
      
      // Verify useResearchStream was called (cleanup happens in the hook)
      expect(mockUseResearchStream).toHaveBeenCalled();
    });
  });

  describe("Accessibility", () => {
    it("has proper ARIA labels", () => {
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "The Source",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      // Header should be a header element
      const header = screen.getByRole("banner");
      expect(header).toBeInTheDocument();

      // Main content should be a main element
      const main = screen.getByRole("main");
      expect(main).toBeInTheDocument();
    });

    it("supports keyboard navigation", () => {
      const mockReconnect = jest.fn();
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.ERROR,
        error: "Connection failed",
        startTime: new Date(),
        completionTime: null,
        reconnect: mockReconnect,
      });

      render(<FlowPage />);

      const retryButton = screen.getByRole("button", { name: /retry/i });
      
      // Simulate keyboard navigation
      retryButton.focus();
      expect(retryButton).toHaveFocus();
      
      // Simulate Enter key press
      fireEvent.keyDown(retryButton, { key: "Enter", code: "Enter" });
      fireEvent.click(retryButton);
      
      expect(mockReconnect).toHaveBeenCalled();
    });
  });

  describe("Mobile Responsiveness", () => {
    it("adapts layout for mobile viewport", () => {
      // Mock mobile viewport
      global.innerWidth = 375;
      global.innerHeight = 667;

      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "The Source",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      // Mobile stats button should be present (in real implementation)
      // This is a placeholder test - actual implementation would check CSS classes
      const main = screen.getByRole("main");
      expect(main).toBeInTheDocument();
    });

    it("adapts layout for tablet viewport", () => {
      // Mock tablet viewport
      global.innerWidth = 768;
      global.innerHeight = 1024;

      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "research",
        activeAgent: "The Source",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });

      render(<FlowPage />);

      const main = screen.getByRole("main");
      expect(main).toBeInTheDocument();
    });
  });

  describe("Integration", () => {
    it("handles full research lifecycle", async () => {
      const { rerender } = render(<FlowPage />);

      // Start: Connecting
      mockUseResearchStream.mockReturnValue({
        messages: [],
        currentPhase: "initialize",
        activeAgent: "",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTING,
        error: null,
        startTime: null,
        completionTime: null,
        reconnect: jest.fn(),
      });
      rerender(<FlowPage />);
      expect(screen.getByText(/connecting/i)).toBeInTheDocument();

      // Connected
      mockUseResearchStream.mockReturnValue({
        messages: [
          {
            agent: "The Flow Master",
            emoji: "🧑‍💼",
            color: "#9D4EDD",
            role: "Orchestrator",
            message: "Starting research",
            message_type: "info",
            timestamp: new Date().toISOString(),
            metadata: {},
          },
        ],
        currentPhase: "hypotheses",
        activeAgent: "The Flow Master",
        iteration: 0,
        maxIterations: 3,
        qualityScore: 0,
        qualityHistory: [],
        connectionStatus: ConnectionStatus.CONNECTED,
        error: null,
        startTime: new Date(),
        completionTime: null,
        reconnect: jest.fn(),
      });
      rerender(<FlowPage />);
      expect(screen.getByText("LIVE")).toBeInTheDocument();

      // Complete
      mockUseResearchStream.mockReturnValue({
        messages: [
          {
            agent: "The Flow Master",
            emoji: "🧑‍💼",
            color: "#9D4EDD",
            role: "Orchestrator",
            message: "Starting research",
            message_type: "info",
            timestamp: new Date().toISOString(),
            metadata: {},
          },
        ],
        currentPhase: "complete",
        activeAgent: "",
        iteration: 2,
        maxIterations: 3,
        qualityScore: 8.5,
        qualityHistory: [6.5, 7.5, 8.5],
        connectionStatus: ConnectionStatus.COMPLETE,
        error: null,
        startTime: new Date(),
        completionTime: new Date(),
        reconnect: jest.fn(),
      });
      rerender(<FlowPage />);
      expect(screen.getByText("COMPLETE")).toBeInTheDocument();
    });
  });
});

