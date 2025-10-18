/**
 * Test Utilities
 * 
 * Common test helpers and utilities for FLUX frontend tests
 */

import React, { ReactElement } from "react";
import { render, RenderOptions } from "@testing-library/react";
import { ConnectionStatus } from "../lib/api";

// Mock data generators

/**
 * Create a mock agent message
 */
export function createMockMessage(overrides?: Partial<any>) {
  return {
    agent: "The Flow Master",
    emoji: "🧑‍💼",
    color: "#9D4EDD",
    role: "Orchestrator",
    message: "Test message",
    message_type: "info",
    timestamp: new Date().toISOString(),
    metadata: {},
    ...overrides,
  };
}

/**
 * Create a mock research stream state
 */
export function createMockStreamState(overrides?: Partial<any>) {
  return {
    messages: [],
    currentPhase: "initialize",
    activeAgent: "",
    iteration: 0,
    maxIterations: 3,
    qualityScore: 0,
    qualityHistory: [],
    connectionStatus: ConnectionStatus.IDLE,
    error: null,
    startTime: null,
    completionTime: null,
    reconnect: jest.fn(),
    ...overrides,
  };
}

/**
 * Create mock messages for a full research cycle
 */
export function createResearchCycleMessages() {
  return [
    createMockMessage({
      agent: "The Flow Master",
      message: "Starting research on quantum computing",
      phase: "initialize",
    }),
    createMockMessage({
      agent: "The Current",
      emoji: "💡",
      color: "#00D9FF",
      message: "Generated 3 hypotheses about quantum entanglement",
      phase: "hypotheses",
      metadata: {
        hypotheses: [
          { text: "Quantum entanglement enables instant communication", confidence: 75 },
          { text: "Entanglement breaks down over long distances", confidence: 60 },
          { text: "Temperature affects entanglement stability", confidence: 85 },
        ],
      },
    }),
    createMockMessage({
      agent: "The Source",
      emoji: "📚",
      color: "#FFA500",
      message: "Found 12 relevant research papers",
      phase: "research",
      metadata: {
        sources: [
          {
            title: "Quantum Entanglement in Superconducting Qubits",
            url: "https://example.com/paper1",
            year: 2023,
            authors: ["Smith, J.", "Doe, A."],
          },
          {
            title: "Temperature Effects on Quantum Coherence",
            url: "https://example.com/paper2",
            year: 2024,
            authors: ["Johnson, M."],
          },
        ],
      },
    }),
    createMockMessage({
      agent: "The Channel",
      emoji: "🔬",
      color: "#06FFA5",
      message: "Designed 5 experimental protocols",
      phase: "experiments",
      metadata: {
        experiments: [
          { name: "Temperature gradient test", methodology: "Controlled cooling" },
          { name: "Distance variation test", methodology: "Fiber optic extension" },
        ],
      },
    }),
    createMockMessage({
      agent: "The Filter",
      emoji: "🛡️",
      color: "#FF4444",
      message: "Quality evaluation complete",
      phase: "critique",
      metadata: {
        quality_score: 7.5,
        issues: ["Need more recent sources", "Hypothesis 2 lacks supporting evidence"],
      },
    }),
    createMockMessage({
      agent: "The Confluence",
      emoji: "✍️",
      color: "#6366F1",
      message: "Research paper synthesis complete",
      phase: "synthesis",
    }),
  ];
}

/**
 * Simulate a viewport size change
 */
export function setViewportSize(width: number, height: number) {
  Object.defineProperty(window, "innerWidth", {
    writable: true,
    configurable: true,
    value: width,
  });
  Object.defineProperty(window, "innerHeight", {
    writable: true,
    configurable: true,
    value: height,
  });
  
  // Trigger resize event
  window.dispatchEvent(new Event("resize"));
}

/**
 * Common viewport sizes
 */
export const VIEWPORTS = {
  mobile: { width: 375, height: 667 }, // iPhone SE
  tablet: { width: 768, height: 1024 }, // iPad
  desktop: { width: 1920, height: 1080 }, // Full HD
};

/**
 * Wait for a condition with timeout
 */
export async function waitForCondition(
  condition: () => boolean,
  timeout: number = 5000,
  interval: number = 100
): Promise<void> {
  const startTime = Date.now();
  
  while (!condition()) {
    if (Date.now() - startTime > timeout) {
      throw new Error(`Timeout waiting for condition after ${timeout}ms`);
    }
    await new Promise((resolve) => setTimeout(resolve, interval));
  }
}

/**
 * Simulate SSE events
 */
export class MockEventSource {
  url: string;
  readyState: number;
  onopen: ((event: any) => void) | null;
  onmessage: ((event: any) => void) | null;
  onerror: ((event: any) => void) | null;
  eventHandlers: Map<string, ((event: any) => void)[]>;

  constructor(url: string) {
    this.url = url;
    this.readyState = 0; // CONNECTING
    this.onopen = null;
    this.onmessage = null;
    this.onerror = null;
    this.eventHandlers = new Map();
  }

  addEventListener(event: string, handler: (event: any) => void) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }

  removeEventListener(event: string, handler: (event: any) => void) {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  dispatchEvent(event: any) {
    const handlers = this.eventHandlers.get(event.type);
    if (handlers) {
      handlers.forEach((handler) => handler(event));
    }
    return true;
  }

  close() {
    this.readyState = 2; // CLOSED
  }

  // Helper methods for testing
  simulateOpen() {
    this.readyState = 1; // OPEN
    const event = new Event("open");
    if (this.onopen) this.onopen(event);
    this.dispatchEvent(event);
  }

  simulateMessage(data: any, eventType: string = "message") {
    const event = {
      type: eventType,
      data: typeof data === "string" ? data : JSON.stringify(data),
    };
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.forEach((handler) => handler(event));
    }
  }

  simulateError(error?: Error) {
    const event = { type: "error", error };
    if (this.onerror) this.onerror(event);
    this.dispatchEvent(event);
  }
}

/**
 * Create a mock EventSource for testing
 */
export function createMockEventSource() {
  return MockEventSource;
}

/**
 * Custom render with providers (if needed in future)
 */
interface CustomRenderOptions extends Omit<RenderOptions, "wrapper"> {
  // Add any providers here in the future
}

export function customRender(
  ui: ReactElement,
  options?: CustomRenderOptions
) {
  return render(ui, { ...options });
}

// Re-export everything from React Testing Library
export * from "@testing-library/react";
export { customRender as render };

/**
 * Accessibility test helpers
 */
export function checkAccessibility(container: HTMLElement) {
  // Check for alt text on images
  const images = container.querySelectorAll("img");
  images.forEach((img) => {
    if (!img.alt && !img.getAttribute("aria-label")) {
      console.warn("Image without alt text or aria-label:", img);
    }
  });

  // Check for form labels
  const inputs = container.querySelectorAll("input, textarea, select");
  inputs.forEach((input) => {
    const id = input.id;
    if (id) {
      const label = container.querySelector(`label[for="${id}"]`);
      if (!label && !input.getAttribute("aria-label")) {
        console.warn("Form input without label:", input);
      }
    }
  });

  // Check for button text
  const buttons = container.querySelectorAll("button");
  buttons.forEach((button) => {
    if (
      !button.textContent?.trim() &&
      !button.getAttribute("aria-label") &&
      !button.getAttribute("aria-labelledby")
    ) {
      console.warn("Button without accessible text:", button);
    }
  });
}

/**
 * Performance testing helpers
 */
export function measureRenderTime(
  renderFn: () => void,
  iterations: number = 10
): number {
  const times: number[] = [];

  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    renderFn();
    const end = performance.now();
    times.push(end - start);
  }

  const average = times.reduce((a, b) => a + b, 0) / times.length;
  return average;
}

/**
 * Mock console methods for testing
 */
export function mockConsole() {
  const originalConsole = {
    log: console.log,
    warn: console.warn,
    error: console.error,
  };

  const mocks = {
    log: jest.spyOn(console, "log").mockImplementation(() => {}),
    warn: jest.spyOn(console, "warn").mockImplementation(() => {}),
    error: jest.spyOn(console, "error").mockImplementation(() => {}),
  };

  return {
    mocks,
    restore: () => {
      console.log = originalConsole.log;
      console.warn = originalConsole.warn;
      console.error = originalConsole.error;
    },
  };
}

