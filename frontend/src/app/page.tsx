"use client";

import React, { useState, useEffect, useRef } from "react";

interface AgentMessage {
  agent_id: string;
  agent_name: string;
  message_type: string;
  content: string;
  confidence: number;
  recommendation: string;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const [selectedAsset, setSelectedAsset] = useState<string>("BTC");
  const [customAsset, setCustomAsset] = useState("");
  
  const [marketState, setMarketState] = useState<any>(null);
  const [debateTranscript, setDebateTranscript] = useState<AgentMessage[]>([]);
  const [votingTally, setVotingTally] = useState<any>(null);
  const [vetoVerification, setVetoVerification] = useState<any>(null);
  const [executionDecision, setExecutionDecision] = useState<any>(null);
  
  const [isSimulating, setIsSimulating] = useState(false);
  const [apiStatus, setApiStatus] = useState<"connected" | "offline">("connected");
  
  const debateEndRef = useRef<HTMLDivElement>(null);
  
  // Auto scroll debate
  useEffect(() => {
    debateEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [debateTranscript]);

  const triggerLiveDebate = (symbol: string) => {
    if (isSimulating) return;
    setIsSimulating(true);
    
    // Reset state
    setMarketState(null);
    setDebateTranscript([]);
    setVotingTally(null);
    setVetoVerification(null);
    setExecutionDecision(null);
    
    const streamUrl = `${BACKEND_URL}/api/stream/run`;
    
    fetch(streamUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol })
    }).then(async (response) => {
      if (!response.body) return;
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let done = false;
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value);
          const lines = chunk.split("\n\n");
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.substring(6));
                handleStreamEvent(data);
              } catch (e) {
                console.error("Failed to parse SSE", e);
              }
            }
          }
        }
      }
      setIsSimulating(false);
    }).catch((err) => {
      console.error("Stream failed", err);
      setIsSimulating(false);
      setApiStatus("offline");
    });
  };

  const handleStreamEvent = (event: any) => {
    switch (event.type) {
      case "MARKET_DATA":
        setMarketState(event.data);
        break;
      case "AGENT_MESSAGE":
        setDebateTranscript(prev => [...prev, event.data]);
        break;
      case "VOTING_COMPLETE":
        setVotingTally(event.data);
        break;
      case "RISK_ASSESSMENT":
        setVetoVerification(event.data);
        break;
      case "EXECUTION_DECISION":
        setExecutionDecision(event.data);
        break;
      case "STREAM_COMPLETE":
        setIsSimulating(false);
        break;
      case "ERROR":
        console.error("Backend Error:", event.data);
        setIsSimulating(false);
        break;
    }
  };

  const getAgentColor = (name: string) => {
    if (name.includes("Technical")) return "bg-blue-100 text-blue-700 border-blue-200";
    if (name.includes("News")) return "bg-purple-100 text-purple-700 border-purple-200";
    if (name.includes("Quant")) return "bg-indigo-100 text-indigo-700 border-indigo-200";
    if (name.includes("Risk")) return "bg-red-100 text-red-700 border-red-200";
    if (name.includes("Execution")) return "bg-emerald-100 text-emerald-700 border-emerald-200";
    return "bg-gray-100 text-gray-700 border-gray-200";
  };

  const getActionColor = (action: string) => {
    if (action === "BUY") return "text-emerald-600 bg-emerald-50 border-emerald-200";
    if (action === "SELL") return "text-red-600 bg-red-50 border-red-200";
    return "text-gray-600 bg-gray-50 border-gray-200";
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-blue-200 selection:text-blue-900">
      
      {/* HEADER */}
      <header className="flex items-center justify-between border-b border-gray-200 bg-white py-4 px-6 shrink-0 shadow-sm z-10">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-600 text-white font-bold shadow-sm">
              C
            </div>
            <h1 className="text-xl font-bold tracking-tight text-gray-900">Council</h1>
          </div>
          <div className="hidden h-6 w-[1px] bg-gray-200 md:block"></div>
          <span className="hidden text-sm font-medium text-gray-500 md:inline">
            Autonomous Investment Committee
          </span>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-200">
            <span className={`h-2.5 w-2.5 rounded-full ${apiStatus === "connected" ? "bg-emerald-500" : "bg-red-500"} ${isSimulating ? 'animate-pulse' : ''}`}></span>
            <span className="text-xs font-semibold text-gray-600">
              {apiStatus === "connected" ? "Live Connected" : "Offline"}
            </span>
          </div>
        </div>
      </header>

      {/* MAIN LAYOUT */}
      <main className="flex-1 max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 min-h-0">
        
        {/* LEFT COLUMN: Controls & Market Data */}
        <section className="lg:col-span-4 flex flex-col gap-6">
          
          {/* ASSET SELECTION */}
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider mb-4 flex items-center justify-between">
              Target Asset
              {isSimulating && <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">ANALYZING...</span>}
            </h2>
            <div className="flex flex-col gap-3">
              <div className="flex gap-2">
                {["BTC", "ETH", "SOL", "DOGE"].map(asset => (
                  <button 
                    key={asset}
                    onClick={() => { setSelectedAsset(asset); triggerLiveDebate(asset); }}
                    disabled={isSimulating}
                    className={`flex-1 py-2 text-sm font-semibold rounded-lg border transition-all ${
                      selectedAsset === asset && !isSimulating 
                        ? "border-blue-600 bg-blue-50 text-blue-700 shadow-sm" 
                        : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    }`}
                  >
                    {asset}
                  </button>
                ))}
              </div>
              <div className="flex gap-2 mt-2">
                <input 
                  type="text" 
                  placeholder="Custom Symbol (e.g. XRP)" 
                  value={customAsset}
                  onChange={(e) => setCustomAsset(e.target.value.toUpperCase())}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button 
                  onClick={() => {
                    if(customAsset) {
                      setSelectedAsset(customAsset);
                      triggerLiveDebate(customAsset);
                    }
                  }}
                  disabled={isSimulating || !customAsset}
                  className="px-4 py-2 bg-gray-900 text-white text-sm font-semibold rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-colors"
                >
                  Analyze
                </button>
              </div>
            </div>
          </div>

          {/* LIVE MARKET DATA */}
          {marketState && (
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm animate-in fade-in slide-in-from-bottom-2">
              <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider mb-4 border-b border-gray-100 pb-2">
                Live Bitget Data
              </h2>
              <div className="grid grid-cols-2 gap-y-4 gap-x-2">
                <div>
                  <span className="text-xs font-medium text-gray-500">Symbol</span>
                  <div className="text-lg font-bold text-gray-900">{marketState.symbol}/USDT</div>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500">Price</span>
                  <div className="text-lg font-bold text-blue-600">${marketState.current_price.toLocaleString()}</div>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500">24H Volatility</span>
                  <div className={`text-sm font-bold ${(marketState.volatility * 100) > 15 ? 'text-red-600' : 'text-emerald-600'}`}>
                    {(marketState.volatility * 100).toFixed(2)}%
                  </div>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500">Market Condition</span>
                  <div className="text-sm font-bold text-gray-700 capitalize">
                    {marketState.market_conditions}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* RISK & EXECUTION SUMMARY */}
          {vetoVerification && (
            <div className={`bg-white border rounded-xl p-5 shadow-sm animate-in zoom-in-95 ${vetoVerification.approved ? 'border-emerald-200' : 'border-red-300'}`}>
              <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider mb-3">
                Risk Manager Decision
              </h2>
              <div className={`p-3 rounded-lg border ${vetoVerification.approved ? 'bg-emerald-50 border-emerald-100 text-emerald-800' : 'bg-red-50 border-red-100 text-red-800'}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold">{vetoVerification.approved ? '✅ APPROVED' : '🚫 VETOED'}</span>
                  <span className="text-xs bg-white px-2 py-0.5 rounded-full border opacity-80">Score: {vetoVerification.risk_score}</span>
                </div>
                <p className="text-sm">{vetoVerification.veto_reason}</p>
              </div>
            </div>
          )}

        </section>

        {/* RIGHT COLUMN: Live Debate Stream */}
        <section className="lg:col-span-8 flex flex-col bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden min-h-[600px]">
          
          <div className="bg-gray-50 border-b border-gray-200 py-3 px-5 flex justify-between items-center shrink-0">
            <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isSimulating ? 'bg-blue-500 animate-pulse' : 'bg-gray-400'}`}></div>
              Live Committee Debate
            </h2>
            {isSimulating && <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded-md">Agents Arguing...</span>}
          </div>

          <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
            {debateTranscript.length === 0 && !isSimulating ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400 gap-3">
                <svg className="w-12 h-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                </svg>
                <p>Select an asset to begin live analysis.</p>
              </div>
            ) : (
              debateTranscript.map((msg, i) => (
                <div key={i} className="flex flex-col gap-1 max-w-[85%] animate-in fade-in slide-in-from-bottom-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${getAgentColor(msg.agent_name)}`}>
                      {msg.agent_name}
                    </span>
                    <span className="text-[10px] font-medium text-gray-400 uppercase tracking-widest">{msg.message_type}</span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${getActionColor(msg.recommendation)}`}>
                      {msg.recommendation} {(msg.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="bg-gray-50 border border-gray-100 text-gray-700 text-sm p-3 rounded-lg rounded-tl-none shadow-sm leading-relaxed">
                    {msg.content}
                  </div>
                </div>
              ))
            )}

            {/* Voting Consensus Block */}
            {votingTally && (
              <div className="my-4 p-4 border border-blue-200 bg-blue-50 rounded-xl flex flex-col gap-3">
                <h3 className="text-xs font-bold text-blue-800 uppercase tracking-wider text-center">Voting Concluded</h3>
                <div className="flex justify-center gap-4">
                  {Object.entries(votingTally.votes || {}).map(([agent, v]: any, idx) => (
                    <div key={idx} className="flex flex-col items-center">
                      <span className="text-[10px] text-blue-600/70 font-medium">{agent.replace("_", " ").toUpperCase()}</span>
                      <span className={`text-sm font-bold ${v.vote === 'BUY' ? 'text-emerald-600' : v.vote === 'SELL' ? 'text-red-600' : 'text-gray-600'}`}>{v.vote}</span>
                    </div>
                  ))}
                </div>
                <div className="text-center pt-2 border-t border-blue-200/50">
                  <span className="text-xs text-blue-700 font-medium">Consensus Action: </span>
                  <span className="text-sm font-black text-blue-900">{votingTally.proposed_action}</span>
                </div>
              </div>
            )}

            {/* Final Execution Block */}
            {executionDecision && (
              <div className="mt-2 p-5 border border-gray-900 bg-gray-900 text-white rounded-xl shadow-lg">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-gray-400">Execution Agent Synthesis</h3>
                  <div className={`px-3 py-1 rounded font-bold text-sm ${executionDecision.action === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : executionDecision.action === 'SELL' ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-300'}`}>
                    FINAL: {executionDecision.action}
                  </div>
                </div>
                <p className="text-sm text-gray-300 leading-relaxed mb-4">
                  {executionDecision.reasoning}
                </p>
                {executionDecision.action !== 'HOLD' && executionDecision.position_size && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-800 text-sm">
                    <div>
                      <span className="block text-gray-500 text-xs mb-1">Entry Price</span>
                      <span className="font-mono text-white">${executionDecision.position_size.entry_price?.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="block text-gray-500 text-xs mb-1">Target</span>
                      <span className="font-mono text-emerald-400">${executionDecision.position_size.target_price?.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="block text-gray-500 text-xs mb-1">Stop Loss</span>
                      <span className="font-mono text-red-400">${executionDecision.position_size.stop_loss?.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="block text-gray-500 text-xs mb-1">Portfolio Allocation</span>
                      <span className="font-mono text-white">{executionDecision.position_size.percentage_of_portfolio?.toFixed(1)}%</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div ref={debateEndRef} className="h-1" />
          </div>
        </section>

      </main>
    </div>
  );
}
