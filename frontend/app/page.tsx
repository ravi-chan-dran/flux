"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const EXAMPLE_QUESTIONS = [
    "How does quantum entanglement work?",
    "What are the latest advances in quantum computing?",
    "Explain the relationship between entropy and information theory",
    "How do neural networks learn representations?",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    setLoading(true);
    
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${API_URL}/api/research/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: question.trim() }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Navigate to flow page with question as query parameter
      const encodedQuestion = encodeURIComponent(question.trim());
      router.push(`/flow/${data.research_id}?question=${encodedQuestion}`);
    } catch (error) {
      console.error("Failed to start research:", error);
      alert("Failed to start research. Please make sure the backend is running on http://localhost:8000");
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-background">
      <div className="relative z-10 container mx-auto px-4 py-16">
        {/* Top Navigation */}
        <div className="absolute top-8 right-8">
          <button
            onClick={() => router.push("/research")}
            className="px-6 py-3 bg-background-light hover:bg-background-lighter border border-gray-700 hover:border-primary-500 rounded-lg text-gray-300 hover:text-primary-400 transition-all flex items-center gap-2"
          >
            <span>📚</span>
            <span>Research Archive</span>
          </button>
        </div>

        {/* Header */}
        <div className="text-center mb-16 animate-slide-up">
          <h1 className="text-8xl font-bold glow-text mb-8">
            FLUX
          </h1>
          <h2 className="text-4xl font-bold text-gray-100 mb-4">
            Research in Motion
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Multi-agent AI research system powered by orbital iteration through specialized agents
          </p>
        </div>

        {/* Research Input */}
        <div className="max-w-4xl mx-auto mb-16">
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
              className="w-full btn-primary text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Starting Research..." : "Start Research"}
            </button>
          </form>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {[
            { label: "AI Agents", value: "6", icon: "🤖" },
            { label: "Research Phases", value: "5", icon: "🔄" },
            { label: "Data Sources", value: "3+", icon: "📚" },
          ].map((stat, index) => (
            <div key={index} className="card text-center hover:border-primary-500 transition-all">
              <div className="text-4xl mb-2">{stat.icon}</div>
              <div className="text-3xl font-bold text-primary-400 mb-1">{stat.value}</div>
              <div className="text-gray-400">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Agent Info */}
        <div className="max-w-6xl mx-auto mt-16">
          <h3 className="text-2xl font-bold text-center text-gray-100 mb-8">
            The Research Team
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { name: "Flow Master", emoji: "🧑‍💼", role: "Orchestrator", color: "#9333EA" },
              { name: "The Current", emoji: "💡", role: "Hypothesis Generator", color: "#06B6D4" },
              { name: "The Source", emoji: "📚", role: "Research Searcher", color: "#F59E0B" },
              { name: "The Channel", emoji: "🔬", role: "Experiment Designer", color: "#14B8A6" },
              { name: "The Filter", emoji: "🛡️", role: "Quality Critic", color: "#EF4444" },
              { name: "The Confluence", emoji: "✍️", role: "Paper Synthesizer", color: "#6366F1" },
            ].map((agent, index) => (
              <div 
                key={index} 
                className="card text-center hover:border-primary-500 transition-all cursor-pointer"
                style={{ borderColor: `${agent.color}40` }}
              >
                <div className="text-5xl mb-3">{agent.emoji}</div>
                <h4 className="text-lg font-semibold text-gray-100 mb-1">{agent.name}</h4>
                <p className="text-sm text-gray-400">{agent.role}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Backend Status Check */}
        <div className="max-w-4xl mx-auto mt-16">
          <div className="card bg-background-light/50 border-primary-500/30">
            <p className="text-sm text-gray-400 text-center">
              💡 <strong>Note:</strong> Make sure the backend is running on{" "}
              <code className="text-primary-400 bg-background px-2 py-1 rounded">
                http://localhost:8000
              </code>
              <br />
              Run <code className="text-primary-400 bg-background px-2 py-1 rounded">python start.py</code> from the project root
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

