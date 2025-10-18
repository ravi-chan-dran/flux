"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { listResearch } from "@/lib/api";
import type { PaperListItem } from "@/lib/types";

export default function ResearchArchivePage() {
  const router = useRouter();
  const [papers, setPapers] = useState<PaperListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<"date" | "quality">("date");

  useEffect(() => {
    loadPapers();
  }, []);

  const loadPapers = async () => {
    try {
      setLoading(true);
      const data = await listResearch();
      setPapers(data.papers || []);
      setError(null);
    } catch (err) {
      console.error("Failed to load papers:", err);
      setError("Failed to load research papers. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const sortedPapers = [...papers].sort((a, b) => {
    if (sortBy === "date") {
      return new Date(b.completed_at || 0).getTime() - new Date(a.completed_at || 0).getTime();
    } else {
      return (b.quality_score || 0) - (a.quality_score || 0);
    }
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getQualityColor = (score: number) => {
    if (score >= 8) return "text-green-400";
    if (score >= 6) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-background-light border-b border-gray-800">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push("/")}
                className="text-gray-400 hover:text-gray-200 transition-colors"
              >
                ← Back
              </button>
              <div className="h-6 w-px bg-gray-700"></div>
              <h1 className="text-3xl font-bold glow-text">Research Archive</h1>
            </div>
            <button
              onClick={() => router.push("/")}
              className="btn-primary"
            >
              + New Research
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12">
        {/* Stats and Sort */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div className="flex items-center gap-6">
            <div>
              <p className="text-sm text-gray-400">Total Research Papers</p>
              <p className="text-3xl font-bold text-primary-400">{papers.length}</p>
            </div>
            {papers.length > 0 && (
              <div>
                <p className="text-sm text-gray-400">Average Quality</p>
                <p className="text-3xl font-bold text-primary-400">
                  {(papers.reduce((sum, p) => sum + (p.quality_score || 0), 0) / papers.length).toFixed(1)}
                </p>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-400">Sort by:</span>
            <button
              onClick={() => setSortBy("date")}
              className={`px-4 py-2 rounded-lg transition-all ${
                sortBy === "date"
                  ? "bg-primary-500 text-white"
                  : "bg-background-light text-gray-400 hover:text-gray-200"
              }`}
            >
              Date
            </button>
            <button
              onClick={() => setSortBy("quality")}
              className={`px-4 py-2 rounded-lg transition-all ${
                sortBy === "quality"
                  ? "bg-primary-500 text-white"
                  : "bg-background-light text-gray-400 hover:text-gray-200"
              }`}
            >
              Quality
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mb-4"></div>
            <p className="text-gray-400">Loading research papers...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="card bg-red-500/10 border-red-500/50 text-center py-12">
            <div className="text-6xl mb-4">⚠️</div>
            <h3 className="text-xl font-semibold text-red-400 mb-2">Error Loading Papers</h3>
            <p className="text-gray-400 mb-6">{error}</p>
            <button onClick={loadPapers} className="btn-primary">
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && papers.length === 0 && (
          <div className="card text-center py-20">
            <div className="text-8xl mb-6">📚</div>
            <h3 className="text-2xl font-semibold text-gray-200 mb-3">No Research Papers Yet</h3>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              Start your first research to see it appear here. All completed research will be saved
              and accessible from this archive.
            </p>
            <button
              onClick={() => router.push("/")}
              className="btn-primary text-lg"
            >
              Start Your First Research →
            </button>
          </div>
        )}

        {/* Papers Grid */}
        {!loading && !error && papers.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedPapers.map((paper) => (
              <div
                key={paper.research_id}
                className="card hover:border-primary-500 transition-all cursor-pointer group"
                onClick={() => router.push(`/papers/${paper.research_id}`)}
              >
                {/* Quality Badge */}
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-gray-500 font-mono">
                    {paper.research_id.substring(0, 16)}...
                  </span>
                  {paper.quality_score !== undefined && (
                    <div
                      className={`flex items-center gap-1 px-2 py-1 rounded-full bg-background text-xs font-semibold ${getQualityColor(
                        paper.quality_score
                      )}`}
                    >
                      <span>⭐</span>
                      <span>{paper.quality_score.toFixed(1)}</span>
                    </div>
                  )}
                </div>

                {/* Question */}
                <h3 className="text-lg font-semibold text-gray-100 mb-3 line-clamp-2 group-hover:text-primary-400 transition-colors">
                  {paper.question}
                </h3>

                {/* Metadata */}
                <div className="space-y-2 text-sm text-gray-400">
                  <div className="flex items-center gap-2">
                    <span>📅</span>
                    <span>{paper.completed_at ? formatDate(paper.completed_at) : "Unknown"}</span>
                  </div>
                  {paper.iterations !== undefined && (
                    <div className="flex items-center gap-2">
                      <span>🔄</span>
                      <span>{paper.iterations} orbit(s)</span>
                    </div>
                  )}
                  {paper.sources_count !== undefined && (
                    <div className="flex items-center gap-2">
                      <span>📚</span>
                      <span>{paper.sources_count} sources</span>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="mt-6 pt-4 border-t border-gray-700 flex gap-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/papers/${paper.research_id}`);
                    }}
                    className="flex-1 px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg transition-all text-sm"
                  >
                    View Paper
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(`/papers/${paper.research_id}`, "_blank");
                    }}
                    className="px-4 py-2 bg-background-lighter hover:bg-gray-600 text-gray-300 rounded-lg transition-all text-sm"
                    title="Open in new tab"
                  >
                    ↗
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

