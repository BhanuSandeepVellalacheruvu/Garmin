"use client";

import { useState, useEffect, useRef } from "react";
import useSWR, { mutate } from "swr";
import { Brain, Send, Sparkles, AlertCircle, RefreshCw, MessageSquare } from "lucide-react";
import { fetchAPI, streamChat } from "@/lib/api";
import { Recommendation } from "@/lib/types";

const SUGGESTED_QUESTIONS = [
  "Why did my pace slow down over the last four weeks?",
  "Am I running enough to prepare for a half marathon?",
  "Compare my recent weekly volume with my chronic base.",
  "How did my heart rate change at the same pace?",
  "What should my training week look like?",
  "Am I recovering adequately based on my recent data?",
  "Summarize my training this month.",
  "What are my biggest weaknesses as a runner?",
];

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function CoachPage() {
  const [conversationId, setConversationId] = useState<string>("default-conv");
  const [inputMessage, setInputMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load recommendations
  const { data: recommendations } = useSWR<Recommendation[]>("/ai/recommendations", fetchAPI);

  // Load message history
  const { data: history } = useSWR<ChatMessage[]>(
    conversationId ? `/ai/conversations/${conversationId}/messages` : null,
    fetchAPI
  );

  useEffect(() => {
    if (history) {
      setMessages(history);
    }
  }, [history]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || isStreaming) return;

    setInputMessage("");

    // Optimistically append user message
    const tempUserMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
    };

    const tempAssistantMsg: ChatMessage = {
      id: `assistant-${Date.now()}`,
      role: "assistant",
      content: "",
    };

    setMessages((prev) => [...prev, tempUserMsg, tempAssistantMsg]);
    setIsStreaming(true);

    try {
      let accumulated = "";
      for await (const chunk of streamChat(conversationId, text)) {
        accumulated += chunk;
        setMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
            updated[lastIdx] = { ...updated[lastIdx], content: accumulated };
          }
          return updated;
        });
      }
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        const lastIdx = updated.length - 1;
        if (lastIdx >= 0 && updated[lastIdx].role === "assistant") {
          updated[lastIdx] = {
            ...updated[lastIdx],
            content: `Failed to communicate with AI Coach: ${(err as Error).message}`,
          };
        }
        return updated;
      });
    } finally {
      setIsStreaming(false);
      mutate(`/ai/conversations/${conversationId}/messages`);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <Brain className="h-6 w-6 text-cyan-400" />
          <span>AI Training Coach</span>
        </h1>
        <p className="text-sm text-gray-400">
          Personalized endurance guidance strictly grounded in your Garmin Connect workouts and biometrics.
        </p>
      </div>

      {/* Recommendations Cards on Top */}
      {recommendations && recommendations.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 shrink-0">
          {recommendations.slice(0, 2).map((rec, i) => (
            <div
              key={i}
              className="bg-[#0C1220] border border-gray-800 rounded-xl p-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
                    {rec.title}
                  </span>
                  <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">
                    {rec.confidence} confidence
                  </span>
                </div>
                <p className="text-xs text-gray-300 mb-2">{rec.action}</p>
                <p className="text-[11px] text-gray-500 italic mb-2">{rec.rationale}</p>
              </div>
              <p className="text-[10px] text-gray-500 border-t border-gray-800/80 pt-1.5">
                *Caveat: {rec.caveat}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Chat Area Container */}
      <div className="flex-1 bg-[#0C1220] border border-gray-800 rounded-xl flex flex-col overflow-hidden min-h-0">
        {/* Messages list */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6">
              <div className="h-12 w-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mb-4">
                <Sparkles className="h-6 w-6" />
              </div>
              <h3 className="text-base font-semibold text-white mb-1">
                Ask your Garmin Training Coach
              </h3>
              <p className="text-xs text-gray-400 max-w-md mb-6">
                Your AI coach retrieves your real distance, pacing, acute/chronic load, and sleep records from the database to answer.
              </p>

              {/* Suggested question chips */}
              <div className="flex flex-wrap gap-2 justify-center max-w-2xl">
                {SUGGESTED_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(q)}
                    className="text-xs px-3 py-1.5 rounded-lg bg-gray-900 border border-gray-800 text-gray-300 hover:text-white hover:border-cyan-500/40 transition text-left"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-3 max-w-3xl ${
                  m.role === "user" ? "ml-auto justify-end" : "mr-auto justify-start"
                }`}
              >
                {m.role === "assistant" && (
                  <div className="h-8 w-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 flex items-center justify-center shrink-0 mt-0.5">
                    <Brain className="h-4 w-4" />
                  </div>
                )}
                <div
                  className={`p-4 rounded-xl text-sm leading-relaxed whitespace-pre-wrap ${
                    m.role === "user"
                      ? "bg-cyan-600 text-white rounded-br-none"
                      : "bg-gray-900 border border-gray-800 text-gray-200 rounded-bl-none shadow-sm"
                  }`}
                >
                  {m.content || (
                    <span className="flex items-center gap-1.5 text-xs text-gray-500">
                      <RefreshCw className="h-3 w-3 animate-spin text-cyan-400" />
                      Analyzing training history...
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input box */}
        <div className="p-4 border-t border-gray-800 bg-gray-950/60">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-3"
          >
            <input
              type="text"
              placeholder="Ask a question about your workouts, fatigue, pacing, or race readiness..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              disabled={isStreaming}
              className="flex-1 px-4 py-2.5 rounded-xl bg-gray-900 border border-gray-800 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400"
            />
            <button
              type="submit"
              disabled={isStreaming || !inputMessage.trim()}
              className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 text-gray-950 font-semibold text-xs transition flex items-center gap-2"
            >
              <span>Ask Coach</span>
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
