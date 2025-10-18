"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { getResearchPaper } from "@/lib/api";
import type { Paper } from "@/lib/types";
import ReactMarkdown from "react-markdown";
import { format } from "date-fns";

type Tab = "paper" | "meta" | "conversation";

export default function PaperPage() {
  const params = useParams();
  const router = useRouter();
  const researchId = params.id as string;

  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("paper");

  useEffect(() => {
    loadPaper();
  }, [researchId]);

  const loadPaper = async () => {
    try {
      setLoading(true);
      const data = await getResearchPaper(researchId);
      setPaper(data);
      setError(null);
    } catch (err) {
      console.error("Failed to load paper:", err);
      setError("Failed to load paper. Make sure the backend is running and the paper exists.");
    } finally {
      setLoading(false);
    }
  };

  const downloadPaper = () => {
    if (!paper) return;
    const blob = new Blob([paper.paper], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `research-${researchId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = () => {
    if (!paper) return;
    navigator.clipboard.writeText(paper.paper);
    alert("Paper copied to clipboard!");
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "PPpp");
    } catch {
      return dateString;
    }
  };

  const formatDuration = (startStr: string, endStr: string) => {
    try {
      const start = new Date(startStr).getTime();
      const end = new Date(endStr).getTime();
      const diffMs = end - start;
      const diffMins = Math.floor(diffMs / 60000);
      const diffSecs = Math.floor((diffMs % 60000) / 1000);
      return `${diffMins}m ${diffSecs}s`;
    } catch {
      return "N/A";
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 8) return "text-green-400";
    if (score >= 6) return "text-yellow-400";
    return "text-red-400";
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-primary-500 mb-4"></div>
          <p className="text-gray-400">Loading research paper...</p>
        </div>
      </main>
    );
  }

  if (error || !paper) {
    return (
      <main className="min-h-screen bg-background">
        <div className="container mx-auto px-6 py-12">
          <div className="card bg-red-500/10 border-red-500/50 text-center py-12 max-w-2xl mx-auto">
            <div className="text-6xl mb-4">⚠️</div>
            <h3 className="text-2xl font-semibold text-red-400 mb-3">Failed to Load Paper</h3>
            <p className="text-gray-400 mb-6">{error}</p>
            <div className="flex gap-4 justify-center">
              <button onClick={loadPaper} className="btn-primary">
                Retry
              </button>
              <button onClick={() => router.push("/")} className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all">
                ← Back to Home
              </button>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-background-light border-b border-gray-800 sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push("/research")}
                className="text-gray-400 hover:text-gray-200 transition-colors"
              >
                ← Archive
              </button>
              <div className="h-6 w-px bg-gray-700"></div>
              <div>
                <h1 className="text-xl font-bold text-gray-100">Research Paper</h1>
                <p className="text-xs text-gray-500 font-mono">{researchId}</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              <button
                onClick={copyToClipboard}
                className="px-4 py-2 bg-background-lighter hover:bg-gray-600 text-gray-300 rounded-lg transition-all text-sm flex items-center gap-2"
              >
                📋 Copy
              </button>
              <button
                onClick={downloadPaper}
                className="btn-primary text-sm flex items-center gap-2"
              >
                📥 Download
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mt-4 border-b border-gray-700">
            <button
              onClick={() => setActiveTab("paper")}
              className={`px-4 py-2 text-sm font-medium transition-all relative ${
                activeTab === "paper"
                  ? "text-primary-400"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              📄 Paper
              {activeTab === "paper" && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>
            <button
              onClick={() => setActiveTab("meta")}
              className={`px-4 py-2 text-sm font-medium transition-all relative ${
                activeTab === "meta"
                  ? "text-primary-400"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              📊 Meta-Analysis
              {activeTab === "meta" && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>
            <button
              onClick={() => setActiveTab("conversation")}
              className={`px-4 py-2 text-sm font-medium transition-all relative ${
                activeTab === "conversation"
                  ? "text-primary-400"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              💬 Conversation
              {activeTab === "conversation" && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-6 py-8">
        {/* Paper Tab */}
        {activeTab === "paper" && (
          <div className="max-w-4xl mx-auto">
            <div className="card prose prose-invert prose-primary max-w-none">
              <ReactMarkdown>{paper.paper}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* Meta-Analysis Tab */}
        {activeTab === "meta" && (
          <div className="max-w-6xl mx-auto space-y-8">
            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="card text-center">
                <div className="text-3xl mb-2">⭐</div>
                <div className={`text-2xl font-bold ${getQualityColor(paper.metadata.final_quality_score)}`}>
                  {paper.metadata.final_quality_score.toFixed(1)}
                </div>
                <div className="text-sm text-gray-400">Quality Score</div>
              </div>
              <div className="card text-center">
                <div className="text-3xl mb-2">🔄</div>
                <div className="text-2xl font-bold text-primary-400">
                  {paper.metadata.total_iterations}
                </div>
                <div className="text-sm text-gray-400">Iterations</div>
              </div>
              <div className="card text-center">
                <div className="text-3xl mb-2">⏱️</div>
                <div className="text-2xl font-bold text-primary-400">
                  {formatDuration(paper.metadata.started_at, paper.metadata.completed_at)}
                </div>
                <div className="text-sm text-gray-400">Duration</div>
              </div>
              <div className="card text-center">
                <div className="text-3xl mb-2">💰</div>
                <div className="text-2xl font-bold text-primary-400">
                  ${paper.metadata.total_cost.toFixed(4)}
                </div>
                <div className="text-sm text-gray-400">Cost</div>
              </div>
            </div>

            {/* Research Details */}
            <div className="card">
              <h2 className="text-xl font-bold text-gray-100 mb-4">Research Details</h2>
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-gray-400">Question:</span>
                  <p className="text-gray-100 mt-1">{paper.metadata.question}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-400">Started:</span>
                    <p className="text-gray-100 text-sm">{formatDate(paper.metadata.started_at)}</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-400">Completed:</span>
                    <p className="text-gray-100 text-sm">{formatDate(paper.metadata.completed_at)}</p>
                  </div>
                </div>
                <div>
                  <span className="text-sm text-gray-400">Stop Reason:</span>
                  <p className="text-gray-100 text-sm">{paper.metadata.stop_reason}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-400">Tokens Used:</span>
                  <p className="text-gray-100 text-sm">{paper.metadata.total_tokens_used.toLocaleString()}</p>
                </div>
              </div>
            </div>

            {/* Quality History Chart */}
            {paper.metadata.quality_history && paper.metadata.quality_history.length > 0 && (
              <div className="card">
                <h2 className="text-xl font-bold text-gray-100 mb-4">Quality Score Evolution</h2>
                <div className="relative h-48 flex items-end gap-2">
                  {paper.metadata.quality_history.map((score, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center gap-2">
                      <div
                        className={`w-full rounded-t-lg transition-all ${
                          score >= 8
                            ? "bg-green-500"
                            : score >= 6
                            ? "bg-yellow-500"
                            : "bg-red-500"
                        }`}
                        style={{ height: `${(score / 10) * 100}%` }}
                      />
                      <span className="text-xs text-gray-400">Iter {index + 1}</span>
                      <span className="text-xs font-mono text-gray-300">{score.toFixed(1)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* State Information (if available) */}
            {paper.state && (
              <>
                {/* Hypotheses */}
                {paper.state.hypotheses && paper.state.hypotheses.length > 0 && (
                  <div className="card">
                    <h2 className="text-xl font-bold text-gray-100 mb-4">
                      💡 Hypotheses ({paper.state.hypotheses.length})
                    </h2>
                    <div className="space-y-4">
                      {paper.state.hypotheses.slice(0, 5).map((hyp, index) => (
                        <div key={hyp.id} className="bg-background-lighter p-4 rounded-lg border border-gray-700">
                          <div className="flex items-start justify-between mb-2">
                            <h3 className="font-semibold text-gray-100">{hyp.text}</h3>
                            <span className="text-sm text-cyan-400 font-mono">
                              {(hyp.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                          <p className="text-sm text-gray-400 mb-2">{hyp.reasoning}</p>
                          <p className="text-xs text-gray-500">Test: {hyp.test_approach}</p>
                        </div>
                      ))}
                      {paper.state.hypotheses.length > 5 && (
                        <p className="text-sm text-gray-500 text-center">
                          + {paper.state.hypotheses.length - 5} more hypotheses
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Sources */}
                {paper.state.sources && paper.state.sources.length > 0 && (
                  <div className="card">
                    <h2 className="text-xl font-bold text-gray-100 mb-4">
                      📚 Sources ({paper.state.sources.length})
                    </h2>
                    <div className="space-y-3">
                      {paper.state.sources.slice(0, 10).map((source, index) => (
                        <div key={index} className="bg-background-lighter p-4 rounded-lg border border-gray-700">
                          <div className="flex items-start justify-between mb-2">
                            <h3 className="font-semibold text-gray-100 flex-1">{source.title}</h3>
                            <span className="text-sm text-amber-400">{source.year}</span>
                          </div>
                          <p className="text-sm text-gray-400 mb-2">
                            {source.authors.slice(0, 3).join(", ")}
                            {source.authors.length > 3 && ` +${source.authors.length - 3} more`}
                          </p>
                          <div className="flex items-center gap-3 text-xs text-gray-500">
                            <span>🏷️ {source.source_type}</span>
                            {source.citation_count && <span>📖 {source.citation_count} citations</span>}
                            {source.url && (
                              <a
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary-400 hover:text-primary-300"
                              >
                                🔗 Link
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                      {paper.state.sources.length > 10 && (
                        <p className="text-sm text-gray-500 text-center">
                          + {paper.state.sources.length - 10} more sources
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Conversation Tab */}
        {activeTab === "conversation" && (
          <div className="max-w-4xl mx-auto space-y-4">
            {paper.conversation && paper.conversation.length > 0 ? (
              <>
                <div className="card bg-background-light">
                  <p className="text-sm text-gray-400">
                    Full conversation log with {paper.conversation.length} messages
                  </p>
                </div>
                {paper.conversation.map((msg, index) => (
                  <div key={index} className="card">
                    <div className="flex items-start gap-4">
                      <div
                        className="w-12 h-12 rounded-full flex items-center justify-center text-2xl flex-shrink-0"
                        style={{ backgroundColor: `${msg.color}20`, border: `2px solid ${msg.color}` }}
                      >
                        {msg.emoji}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <span className="font-semibold text-gray-100">{msg.agent}</span>
                            <span className="text-sm text-gray-500 ml-2">{msg.role}</span>
                          </div>
                          <span className="text-xs text-gray-500">
                            {formatDate(msg.timestamp)}
                          </span>
                        </div>
                        <p className="text-gray-300 whitespace-pre-wrap">{msg.message}</p>
                        
                        {/* Metadata */}
                        {msg.metadata && Object.keys(msg.metadata).length > 0 && (
                          <div className="mt-3 p-3 bg-background rounded-lg border border-gray-700">
                            <details>
                              <summary className="text-sm text-gray-400 cursor-pointer hover:text-gray-300">
                                View metadata
                              </summary>
                              <pre className="text-xs text-gray-500 mt-2 overflow-x-auto">
                                {JSON.stringify(msg.metadata, null, 2)}
                              </pre>
                            </details>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </>
            ) : (
              <div className="card text-center py-12">
                <div className="text-6xl mb-4">💬</div>
                <h3 className="text-xl font-semibold text-gray-100 mb-2">No Conversation Log</h3>
                <p className="text-gray-400">
                  Conversation history is not available for this research paper.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
