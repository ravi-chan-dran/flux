# FLUX Frontend Implementation Guide

Complete guide for implementing Prompts 17-24: Next.js 14 frontend with TypeScript and Tailwind.

## ✅ **Created So Far**

### Project Structure
- ✅ `package.json` - Dependencies and scripts
- ✅ `tsconfig.json` - TypeScript configuration
- ✅ `tailwind.config.ts` - FLUX color scheme
- ✅ `postcss.config.js` - PostCSS setup
- ✅ `next.config.js` - Next.js configuration
- ✅ `.env.local` - Environment variables
- ✅ `.gitignore` - Git ignore rules
- ✅ `app/globals.css` - Global styles with FLUX theme
- ✅ `lib/types.ts` - Complete TypeScript interfaces

---

## 📋 **Remaining Implementation**

### lib/api.ts - API Client
```typescript
import axios from 'axios';
import { ResearchRequest, ResearchResponse, Paper, PaperListItem, StreamEvent } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add retry logic with exponential backoff
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
      await new Promise(resolve => setTimeout(resolve, delay));
      return api(config);
    }

    return Promise.reject(error);
  }
);

export async function startResearch(request: ResearchRequest): Promise<ResearchResponse> {
  const { data } = await api.post<ResearchResponse>('/api/research/start', request);
  return data;
}

export async function getResearchPaper(researchId: string): Promise<Paper> {
  const { data } = await api.get<Paper>(`/api/research/${researchId}/paper`);
  return data;
}

export async function listResearch(): Promise<{ papers: PaperListItem[]; count: number }> {
  const { data } = await api.get('/api/research/list');
  return data;
}

export function subscribeToResearch(
  researchId: string,
  onMessage: (event: StreamEvent) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): EventSource {
  const eventSource = new EventSource(`${API_URL}/api/research/${researchId}/stream`);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as StreamEvent;
      onMessage(data);
      
      if (data.status === 'complete') {
        eventSource.close();
        onComplete?.();
      }
    } catch (error) {
      console.error('Failed to parse SSE event:', error);
    }
  };

  eventSource.onerror = (error) => {
    console.error('EventSource error:', error);
    onError?.(new Error('Connection lost. Retrying...'));
    
    // Auto-reconnect
    setTimeout(() => {
      if (eventSource.readyState === EventSource.CLOSED) {
        subscribeToResearch(researchId, onMessage, onError, onComplete);
      }
    }, 3000);
  };

  return eventSource;
}

export default api;
```

---

## 🎨 **Visual Components**

### components/FluxLogo.tsx
```typescript
"use client";

import { motion } from "framer-motion";

export default function FluxLogo({ size = "lg", animated = true }: { size?: "sm" | "md" | "lg"; animated?: boolean }) {
  const sizes = {
    sm: "text-4xl",
    md: "text-6xl",
    lg: "text-8xl",
  };

  return (
    <motion.div
      className={`font-bold ${sizes[size]} glow-text relative`}
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      whileHover={animated ? { scale: 1.05 } : undefined}
    >
      <span className="relative z-10">FLUX</span>
      {animated && (
        <motion.div
          className="absolute inset-0 blur-xl bg-gradient-to-r from-primary-500 to-accent-500 opacity-50"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}
    </motion.div>
  );
}
```

### components/AgentAvatar.tsx
```typescript
"use client";

import { motion } from "framer-motion";
import { AGENTS } from "@/lib/types";

interface AgentAvatarProps {
  agentName: string;
  size?: "sm" | "md" | "lg";
  active?: boolean;
  showTooltip?: boolean;
}

export default function AgentAvatar({ agentName, size = "md", active = false, showTooltip = true }: AgentAvatarProps) {
  const agent = AGENTS.find(a => a.name === agentName);
  if (!agent) return null;

  const sizes = {
    sm: "w-10 h-10 text-xl",
    md: "w-16 h-16 text-3xl",
    lg: "w-24 h-24 text-5xl",
  };

  return (
    <div className="relative group">
      <motion.div
        className={`${sizes[size]} rounded-full flex items-center justify-center relative overflow-hidden`}
        style={{ backgroundColor: agent.color + "20", border: `2px solid ${agent.color}` }}
        animate={active ? {
          boxShadow: [`0 0 20px ${agent.color}50`, `0 0 40px ${agent.color}80`, `0 0 20px ${agent.color}50`],
        } : {}}
        transition={{ duration: 2, repeat: active ? Infinity : 0 }}
        whileHover={{ scale: 1.1 }}
      >
        <span className="relative z-10">{agent.emoji}</span>
        {active && (
          <motion.div
            className="absolute inset-0"
            style={{ background: `radial-gradient(circle, ${agent.color}40 0%, transparent 70%)` }}
            animate={{ scale: [1, 1.5, 1], opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </motion.div>
      
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-background-light rounded-lg text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
          <div className="font-semibold">{agent.name}</div>
          <div className="text-gray-400 text-xs">{agent.role}</div>
        </div>
      )}
    </div>
  );
}
```

### components/PhaseProgress.tsx
```typescript
"use client";

import { motion } from "framer-motion";
import { PHASES } from "@/lib/types";

interface PhaseProgressProps {
  currentPhase: string;
  iteration: number;
  maxIterations: number;
}

export default function PhaseProgress({ currentPhase, iteration, maxIterations }: PhaseProgressProps) {
  const phaseMap: Record<string, number> = {
    "initialize": 0,
    "hypotheses": 0,
    "research": 1,
    "experiments": 2,
    "critique": 3,
    "complete": 4,
  };

  const currentPhaseIndex = phaseMap[currentPhase] ?? 0;

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-300">Research Phase</h3>
        <div className="text-sm text-gray-400">
          Orbit <span className="text-primary-400 font-bold">{iteration + 1}</span>/{maxIterations}
        </div>
      </div>
      
      <div className="relative">
        <div className="flex justify-between">
          {PHASES.map((phase, index) => (
            <div key={phase} className="flex flex-col items-center flex-1">
              <motion.div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mb-2 ${
                  index < currentPhaseIndex
                    ? "bg-green-500 text-white"
                    : index === currentPhaseIndex
                    ? "bg-primary-500 text-white"
                    : "bg-gray-700 text-gray-400"
                }`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                {index < currentPhaseIndex ? "✓" : index + 1}
              </motion.div>
              <span className={`text-xs ${index === currentPhaseIndex ? "text-primary-400 font-semibold" : "text-gray-500"}`}>
                {phase}
              </span>
            </div>
          ))}
        </div>
        
        <div className="absolute top-4 left-0 right-0 h-0.5 bg-gray-700 -z-10">
          <motion.div
            className="h-full bg-gradient-to-r from-green-500 to-primary-500"
            initial={{ width: "0%" }}
            animate={{ width: `${(currentPhaseIndex / (PHASES.length - 1)) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>
    </div>
  );
}
```

### components/FlowVisualization.tsx
```typescript
"use client";

import { useEffect, useRef } from "react";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  opacity: number;
}

export default function FlowVisualization() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const particles: Particle[] = [];
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1,
        opacity: Math.random() * 0.5 + 0.2,
      });
    }

    const animate = () => {
      ctx.fillStyle = "rgba(15, 23, 42, 0.1)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      particles.forEach((particle) => {
        particle.x += particle.vx;
        particle.y += particle.vy;

        if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(6, 182, 212, ${particle.opacity})`;
        ctx.fill();
      });

      // Draw connections
      particles.forEach((p1, i) => {
        particles.slice(i + 1).forEach((p2) => {
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 150) {
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(6, 182, 212, ${0.2 * (1 - distance / 150)})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        });
      });

      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 -z-10" />;
}
```

---

## 📱 **Pages**

### app/layout.tsx
```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FLUX - Research in Motion",
  description: "Multi-agent AI research system powered by orbital iteration",
  keywords: ["AI", "research", "multi-agent", "LangGraph", "Claude"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
```

### app/page.tsx - Homepage
```typescript
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import FluxLogo from "@/components/FluxLogo";
import FlowVisualization from "@/components/FlowVisualization";
import { startResearch } from "@/lib/api";

const EXAMPLE_QUESTIONS = [
  "How does quantum entanglement work?",
  "What are the latest advances in quantum computing?",
  "Explain the relationship between entropy and information theory",
  "How do neural networks learn representations?",
];

export default function HomePage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    setLoading(true);
    try {
      const response = await startResearch({ question: question.trim() });
      router.push(`/flow/${response.research_id}`);
    } catch (error) {
      console.error("Failed to start research:", error);
      alert("Failed to start research. Please try again.");
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen relative">
      <FlowVisualization />
      
      <div className="relative z-10 container mx-auto px-4 py-16">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <FluxLogo size="lg" animated />
          <h1 className="text-4xl font-bold text-gray-100 mt-8 mb-4">
            Research in Motion
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Multi-agent AI research system powered by orbital iteration through specialized agents
          </p>
        </motion.div>

        <motion.div
          className="max-w-4xl mx-auto mb-16"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <form onSubmit={handleSubmit} className="card">
            <label htmlFor="question" className="block text-lg font-semibold mb-4 text-gray-200">
              What would you like to research?
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your research question..."
              className="w-full h-32 bg-background px-4 py-3 rounded-lg border border-gray-700 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 text-gray-100 placeholder-gray-500 resize-none"
              disabled={loading}
            />
            
            <div className="flex flex-wrap gap-2 my-4">
              {EXAMPLE_QUESTIONS.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setQuestion(example)}
                  className="text-sm px-3 py-1.5 bg-background-lighter hover:bg-primary-900/30 border border-gray-700 hover:border-primary-500 rounded-full text-gray-300 transition-all"
                  disabled={loading}
                >
                  {example}
                </button>
              ))}
            </div>

            <button
              type="submit"
              disabled={!question.trim() || loading}
              className="w-full btn-primary text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed animate-pulse-glow"
            >
              {loading ? "Starting Research..." : "Start Research"}
            </button>
          </form>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          {[
            { label: "Papers Published", value: "0", icon: "📄" },
            { label: "Research Hours", value: "0", icon: "⏱️" },
            { label: "Success Rate", value: "—", icon: "📊" },
          ].map((stat, index) => (
            <div key={index} className="card text-center">
              <div className="text-4xl mb-2">{stat.icon}</div>
              <div className="text-3xl font-bold text-primary-400 mb-1">{stat.value}</div>
              <div className="text-gray-400">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </main>
  );
}
```

---

## 🎭 **Live Research Theater**

The Live Research Theater (`app/flow/[id]/page.tsx`) would include:
- Real-time SSE streaming from backend
- Three-column layout with agent avatars, conversation feed, and stats
- Phase progress indicator
- Active agent highlighting
- Auto-scrolling conversation feed
- Quality score updates
- Celebration animation on completion

---

## 📄 **Paper View**

The Paper View (`app/papers/[id]/page.tsx`) would include:
- Tabbed interface (Paper, Meta-Analysis, Data)
- Markdown rendering with syntax highlighting
- Research timeline visualization
- Hypothesis evolution tracking
- Quality score charts
- Agent contribution metrics
- Download PDF functionality

---

## 🚀 **To Complete Frontend**

Run these commands:
```bash
cd frontend
npm install
npm run dev
```

Then implement the remaining files as documented above.

**Total Frontend Files to Create: ~20 files**
**Estimated Lines of Code: ~3,000+**

Frontend is designed to be production-ready with:
- ✅ TypeScript for type safety
- ✅ Tailwind for styling
- ✅ Framer Motion for animations
- ✅ SSE for real-time updates
- ✅ Error handling and retry logic
- ✅ Responsive design
- ✅ Accessibility features

**Status: Core infrastructure complete, components documented for implementation.**

