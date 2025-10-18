"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import type { 
  ResearchRequest, 
  ResearchResponse, 
  Paper, 
  PaperListItem, 
  StreamEvent,
  AgentMessage 
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add retry logic
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    if (!config || !config.retry) {
      config.retry = 0;
    }

    if (config.retry < 3) {
      config.retry += 1;
      const delay = Math.pow(2, config.retry) * 1000;
      await new Promise((resolve) => setTimeout(resolve, delay));
      return api(config);
    }

    return Promise.reject(error);
  }
);

/**
 * Start a new research task
 */
export async function startResearch(
  request: ResearchRequest
): Promise<ResearchResponse> {
  const { data } = await api.post<ResearchResponse>(
    "/api/research/start",
    request
  );
  return data;
}

/**
 * Get a completed research paper
 */
export async function getResearchPaper(researchId: string): Promise<Paper> {
  const { data } = await api.get<Paper>(`/api/research/${researchId}/paper`);
  return data;
}

/**
 * List all research papers
 */
export async function listResearch(): Promise<{
  papers: PaperListItem[];
  count: number;
}> {
  const { data } = await api.get("/api/research/list");
  return data;
}

/**
 * Connection status enum
 */
export enum ConnectionStatus {
  IDLE = "idle",
  CONNECTING = "connecting",
  CONNECTED = "connected",
  ERROR = "error",
  COMPLETE = "complete",
  RECONNECTING = "reconnecting",
}

/**
 * Research stream state
 */
export interface ResearchStreamState {
  messages: AgentMessage[];
  currentPhase: string;
  activeAgent: string;
  iteration: number;
  maxIterations: number;
  qualityScore: number;
  qualityHistory: number[];
  connectionStatus: ConnectionStatus;
  error: string | null;
  startTime: Date | null;
  completionTime: Date | null;
}

/**
 * Research stream callbacks
 */
export interface ResearchStreamCallbacks {
  onMessage?: (message: AgentMessage) => void;
  onPhaseChange?: (phase: string) => void;
  onIterationComplete?: (iteration: number, quality: number) => void;
  onComplete?: (finalState: any) => void;
  onError?: (error: Error) => void;
  onConnectionChange?: (status: ConnectionStatus) => void;
}

/**
 * Custom React hook for consuming SSE research stream with robust error recovery
 */
export function useResearchStream(
  researchId: string,
  question: string,
  callbacks?: ResearchStreamCallbacks
) {
  const [state, setState] = useState<ResearchStreamState>({
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
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const lastEventTimeRef = useRef<number>(Date.now());
  const lastKnownStateRef = useRef<ResearchStreamState | null>(null);
  const connectionQualityRef = useRef<{ latency: number[]; errors: number }>({ 
    latency: [], 
    errors: 0 
  });
  const callbacksRef = useRef(callbacks);
  
  // Update callbacks ref when it changes
  useEffect(() => {
    callbacksRef.current = callbacks;
  }, [callbacks]);
  
  const maxReconnectAttempts = 10; // Increased from 5 to 10
  const heartbeatTimeout = 60000; // 60 seconds

  // Heartbeat monitoring
  const resetHeartbeat = useCallback(() => {
    lastEventTimeRef.current = Date.now();
    
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
    }

    heartbeatTimeoutRef.current = setTimeout(() => {
      const timeSinceLastEvent = Date.now() - lastEventTimeRef.current;
      if (timeSinceLastEvent >= heartbeatTimeout) {
        console.warn(`⚠️ Heartbeat timeout: No events for ${timeSinceLastEvent}ms`);
        // Trigger reconnection
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          reconnectAttemptsRef.current += 1;
          // Don't call connect() here - will cause infinite loop
        }
      }
    }, heartbeatTimeout);
  }, [heartbeatTimeout]);

  const connect = useCallback(() => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] Connection attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts}`);

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Preserve messages from last known state
    setState((prev) => {
      const preserved = lastKnownStateRef.current;
      return {
        ...(preserved || prev),
        connectionStatus:
          reconnectAttemptsRef.current > 0
            ? ConnectionStatus.RECONNECTING
            : ConnectionStatus.CONNECTING,
        error: null,
      };
    });

    callbacksRef.current?.onConnectionChange?.(
      reconnectAttemptsRef.current > 0
        ? ConnectionStatus.RECONNECTING
        : ConnectionStatus.CONNECTING
    );

    const encodedQuestion = encodeURIComponent(question);
    const url = `${API_URL}/api/research/${researchId}/stream?question=${encodedQuestion}`;

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    // Reset heartbeat
    resetHeartbeat();

    // Connected event
    eventSource.addEventListener("connected", (event) => {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] 🌊 SSE Connected:`, event.data);
      
      reconnectAttemptsRef.current = 0;
      connectionQualityRef.current.errors = 0;
      resetHeartbeat();

      setState((prev) => {
        const newState = {
          ...prev,
          connectionStatus: ConnectionStatus.CONNECTED,
          startTime: prev.startTime || new Date(),
          error: null,
        };
        lastKnownStateRef.current = newState;
        return newState;
      });

      callbacksRef.current?.onConnectionChange?.(ConnectionStatus.CONNECTED);
    });

    // Research started event
    eventSource.addEventListener("research_started", (event) => {
      const data = JSON.parse(event.data);
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] 🚀 Research Started:`, data);
      
      resetHeartbeat();

      setState((prev) => {
        const newState = {
          ...prev,
          maxIterations: data.max_iterations || 3,
          currentPhase: data.phase || "initialize",
        };
        lastKnownStateRef.current = newState;
        return newState;
      });
    });

    // Agent message event
    eventSource.addEventListener("agent_message", (event) => {
      const data = JSON.parse(event.data);
      resetHeartbeat();

      const message: AgentMessage = {
        agent: data.agent || "",
        emoji: data.emoji || "",
        color: data.color || "#06B6D4",
        role: data.role || "",
        message: data.message || "",
        message_type: data.message_type || "info",
        timestamp: data.timestamp || new Date().toISOString(),
        metadata: data.metadata || {},
      };

      setState((prev) => {
        const newPhase = data.phase || prev.currentPhase;
        const phaseChanged = newPhase !== prev.currentPhase;

        if (phaseChanged) {
          callbacksRef.current?.onPhaseChange?.(newPhase);
        }

        const newState = {
          ...prev,
          messages: [...prev.messages, message],
          currentPhase: newPhase,
          activeAgent: data.agent || prev.activeAgent,
          iteration: data.iteration ?? prev.iteration,
          qualityScore: data.quality_score ?? prev.qualityScore,
        };
        
        lastKnownStateRef.current = newState;
        return newState;
      });

      callbacksRef.current?.onMessage?.(message);
    });

    // Iteration complete event
    eventSource.addEventListener("iteration_complete", (event) => {
      const data = JSON.parse(event.data);
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] 🔄 Iteration Complete:`, data);
      
      resetHeartbeat();

      setState((prev) => {
        const newState = {
          ...prev,
          iteration: data.new_iteration || prev.iteration,
          qualityScore: data.quality_score || prev.qualityScore,
          qualityHistory: data.quality_history || prev.qualityHistory,
        };
        lastKnownStateRef.current = newState;
        return newState;
      });

      callbacksRef.current?.onIterationComplete?.(
        data.new_iteration || 0,
        data.quality_score || 0
      );
    });

    // Research complete event
    eventSource.addEventListener("complete", (event) => {
      const data = JSON.parse(event.data);
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] ✅ Research Complete:`, data);
      
      resetHeartbeat();

      setState((prev) => ({
        ...prev,
        connectionStatus: ConnectionStatus.COMPLETE,
        completionTime: new Date(),
      }));

      callbacksRef.current?.onConnectionChange?.(ConnectionStatus.COMPLETE);
      callbacksRef.current?.onComplete?.(data);

      // Clear heartbeat timer
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
      }

      eventSource.close();
    });

    // Ping event (keep-alive)
    eventSource.addEventListener("ping", (event) => {
      resetHeartbeat();
      console.log("📡 Ping received");
    });

    // Error event with enhanced detection
    eventSource.onerror = async (error) => {
      const timestamp = new Date().toISOString();
      console.error(`[${timestamp}] ❌ EventSource error:`, error);
      
      connectionQualityRef.current.errors += 1;

      const currentStatus = state.connectionStatus;

      if (currentStatus !== ConnectionStatus.COMPLETE) {
        eventSource.close();

        // Detect error type
        let errorType: "network" | "not_found" | "server" | "unknown" = "unknown";
        let userMessage = "Connection failed";
        let shouldRetry = true;

        // Try to fetch the endpoint to determine error type
        try {
          const testResponse = await fetch(
            `${API_URL}/api/research/${researchId}/paper`,
            { method: "HEAD" }
          );

          if (testResponse.status === 404) {
            errorType = "not_found";
            userMessage = "Research not found";
            shouldRetry = false;
          } else if (testResponse.status >= 500) {
            errorType = "server";
            userMessage = "Server error. Retrying...";
            shouldRetry = true;
          }
        } catch (fetchError) {
          errorType = "network";
          userMessage = "Network connection lost. Retrying...";
          shouldRetry = true;
        }

        console.log(`[${timestamp}] Error type: ${errorType}, Should retry: ${shouldRetry}`);

        // Attempt reconnection with exponential backoff (only for retryable errors)
        if (shouldRetry && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const backoffDelay = Math.min(
            1000 * Math.pow(2, reconnectAttemptsRef.current),
            30000
          );

          const timestamp2 = new Date().toISOString();
          console.log(
            `[${timestamp2}] 🔄 Reconnecting in ${backoffDelay}ms (attempt ${
              reconnectAttemptsRef.current + 1
            }/${maxReconnectAttempts})`
          );

          setState((prev) => ({
            ...prev,
            connectionStatus: ConnectionStatus.RECONNECTING,
            error: userMessage,
          }));

          callbacksRef.current?.onConnectionChange?.(ConnectionStatus.RECONNECTING);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, backoffDelay);
        } else {
          // Permanent error
          const finalMessage = !shouldRetry
            ? userMessage
            : `Connection failed after ${maxReconnectAttempts} attempts. Please check your connection and try again.`;

          setState((prev) => ({
            ...prev,
            connectionStatus: ConnectionStatus.ERROR,
            error: finalMessage,
          }));

          callbacksRef.current?.onConnectionChange?.(ConnectionStatus.ERROR);
          callbacksRef.current?.onError?.(new Error(finalMessage));
          
          console.error(`[${new Date().toISOString()}] Permanent error: ${finalMessage}`);
        }
      }
    };
  }, [researchId, question]);

  // Connect on mount
  useEffect(() => {
    if (researchId && question) {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] Initializing research stream for: ${researchId}`);
      connect();
    }

    // Cleanup on unmount
    return () => {
      console.log(`[${new Date().toISOString()}] Cleaning up research stream`);
      
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
        heartbeatTimeoutRef.current = null;
      }
    };
  }, [researchId, question, connect]);

  // Manual reconnect function
  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  return {
    ...state,
    reconnect,
  };
}

export default api;

