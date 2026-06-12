"use client";

import React, { useState, useEffect, useRef } from "react";

// Types matching schemas.py
interface ReplaySummary {
  session_id: string;
  symbol: string;
  final_action: string;
  confidence_score: number;
  trade_status: string;
  realized_pnl?: number;
  created_at: string;
}

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
  // --- STATE MANAGEMENT ---
  const [selectedAsset, setSelectedAsset] = useState<"BTC" | "ETH">("BTC");
  const [replays, setReplays] = useState<ReplaySummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  
  // Debate & Timeline variables
  const [marketState, setMarketState] = useState<any>({
    symbol: "BTC",
    current_price: 43500.0,
    price_24h_high: 44200.0,
    price_24h_low: 42900.0,
    volume_24h: 125000000.0,
    volatility: 0.22,
    trend_direction: "UP",
    market_news_count: 14,
    market_conditions: "bullish",
  });
  const [initialOpinions, setInitialOpinions] = useState<Record<string, any>>({
    technical_analyst: { recommendation: "BUY", confidence: 80, reasoning: "Golden cross on 4h chart with rising RSI support breakout." },
    news_analyst: { recommendation: "BUY", confidence: 75, reasoning: "Positive sentiment due to heavy ETF net inflows." },
    quant_analyst: { recommendation: "BUY", confidence: 70, reasoning: "Quant pattern breakout matches statistical momentum." }
  });
  const [debateTranscript, setDebateTranscript] = useState<AgentMessage[]>([]);
  const [votingTally, setVotingTally] = useState<any>({
    votes: {
      technical_analyst: { vote: "BUY", weight: 1.2, confidence: 80 },
      quant_analyst: { vote: "BUY", weight: 1.1, confidence: 72 },
      news_analyst: { vote: "BUY", weight: 1.0, confidence: 75 }
    },
    proposed_action: "BUY"
  });
  const [vetoVerification, setVetoVerification] = useState<any>({
    risk_score: 25.0,
    risk_level: "low",
    position_size_recommendation: 15000.0,
    max_position_allowed: 0.15,
    approved: true,
    veto_reason: "Approved: Risk metrics are within safe boundaries."
  });
  const [executionDecision, setExecutionDecision] = useState<any>({
    action: "BUY",
    confidence_score: 84.85,
    confidence_factors: {
      raw_scores: { agent_agreement: 100, risk_score_factor: 75, volatility_factor: 78, sentiment_stability: 75, historical_accuracy: 69 },
      weighted_contributions: { agent_agreement: 40.0, risk_score_factor: 15.0, volatility_factor: 11.7, sentiment_stability: 11.25, historical_accuracy: 6.9 }
    },
    position_size: { percentage_of_portfolio: 12.0, quantity: 0.2758, entry_price: 43500.0, target_price: 46500.0, stop_loss: 41800.0 },
    reasoning: "The committee reached a unanimous agreement to BUY BTC. Strong ETF inflows support technical breakouts, and low volatility metrics authorize high position sizing.",
    key_factors: ["Unanimous consensus", "ETF inflows breakout", "Low risk profile"]
  });
  const [tradeResult, setTradeResult] = useState<any>({
    status: "completed",
    entry_price: 43500.0,
    quantity: 0.2758,
    exit_price: 46500.0,
    exit_timestamp: "2026-06-11T14:30:00Z",
    realized_pnl: 827.40,
    notes: "Target hit. Trade exited automatically at $46,500."
  });

  // Replay Control State
  const [isPlaying, setIsPlaying] = useState(false);
  const [playIndex, setPlayIndex] = useState(0);
  const [fullTranscript, setFullTranscript] = useState<AgentMessage[]>([]);
  const [apiStatus, setApiStatus] = useState<"connected" | "offline">("offline");
  
  // Tab control for right-side panels
  const [activeRightTab, setActiveRightTab] = useState<"replay" | "journal" | "demo">("replay");

  // Simulation (Demo Mode) State
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationStep, setSimulationStep] = useState(0);
  const [simulationLogs, setSimulationLogs] = useState<string[]>([]);
  
  // Refs
  const debateEndRef = useRef<HTMLDivElement>(null);

  // --- FETCH REPLAY SUMMARIES ---
  useEffect(() => {
    async function loadReplays() {
      try {
        const response = await fetch(`${BACKEND_URL}/api/replay`);
        if (response.ok) {
          const data = await response.json();
          setReplays(data);
          setApiStatus("connected");
          if (data.length > 0 && !activeSessionId) {
            loadTimeline(data[0].session_id);
          }
        }
      } catch (err) {
        loggerOfflineFallback();
      }
    }
    loadReplays();
  }, []);

  function loggerOfflineFallback() {
    setApiStatus("offline");
    // Fallback static summaries matching our preloaded JSON
    const staticReplays: ReplaySummary[] = [
      {
        session_id: "d11b34a6-4be4-42f0-9a2c-e1f4864b22c0",
        symbol: "BTC",
        final_action: "BUY",
        confidence_score: 84.85,
        trade_status: "completed",
        realized_pnl: 827.40,
        created_at: new Date(Date.now() - 172800000).toISOString()
      },
      {
        session_id: "bc3f4124-7f12-4cf4-912b-2a21b44b20cf",
        symbol: "ETH",
        final_action: "HOLD",
        confidence_score: 62.65,
        trade_status: "failed",
        realized_pnl: 0.0,
        created_at: new Date(Date.now() - 345600000).toISOString()
      }
    ];
    setReplays(staticReplays);
    if (!activeSessionId) {
      loadLocalTimeline(staticReplays[0].session_id);
    }
  }

  // --- LOAD DETAILED TIMELINE ---
  async function loadTimeline(sessionId: string) {
    if (isSimulating) return;
    try {
      const response = await fetch(`${BACKEND_URL}/api/replay/${sessionId}`);
      if (response.ok) {
        const timeline = await response.json();
        setActiveSessionId(sessionId);
        applyTimelineData(timeline);
      }
    } catch (err) {
      loadLocalTimeline(sessionId);
    }
  }

  function loadLocalTimeline(sessionId: string) {
    setActiveSessionId(sessionId);
    // Local mock data mirroring replay_service.py fallback
    if (sessionId === "d11b34a6-4be4-42f0-9a2c-e1f4864b22c0") {
      applyTimelineData({
        symbol: "BTC",
        market_state: { symbol: "BTC", current_price: 43500.0, price_24h_high: 44200.0, price_24h_low: 42900.0, volume_24h: 125000000.0, volatility: 0.22, trend_direction: "UP", market_news_count: 14, market_conditions: "bullish" },
        initial_opinions: {
          technical_analyst: { recommendation: "BUY", confidence: 80, reasoning: "Golden cross on 4h chart with rising RSI support breakout." },
          news_analyst: { recommendation: "BUY", confidence: 75, reasoning: "Positive sentiment due to heavy ETF net inflows." },
          quant_analyst: { recommendation: "BUY", confidence: 70, reasoning: "Quant pattern breakout matches statistical momentum." }
        },
        debate_transcript: [
          { agent_id: "news_analyst", agent_name: "News Analyst", message_type: "ANALYSIS", content: "Initial Analysis: BUY. Sentiment is highly positive due to heavy ETF net inflows.", confidence: 0.75, recommendation: "BUY" },
          { agent_id: "quant_analyst", agent_name: "Quant Analyst", message_type: "ANALYSIS", content: "Initial Analysis: BUY. Expected value suggests upward bias.", confidence: 0.70, recommendation: "BUY" },
          { agent_id: "technical_analyst", agent_name: "Technical Analyst", message_type: "AGREEMENT", content: "I agree with the News Analyst. The heavy volume breakout matches the structural ETF flows.", confidence: 0.85, recommendation: "BUY" }
        ],
        voting_tally: {
          votes: {
            technical_analyst: { vote: "BUY", weight: 1.2, confidence: 80 },
            quant_analyst: { vote: "BUY", weight: 1.1, confidence: 72 },
            news_analyst: { vote: "BUY", weight: 1.0, confidence: 75 }
          },
          proposed_action: "BUY"
        },
        veto_verification: { risk_score: 25.0, risk_level: "low", position_size_recommendation: 15000.0, max_position_allowed: 0.15, approved: true, veto_reason: "Approved: Risk metrics are within safe boundaries." },
        execution_decision: {
          action: "BUY",
          confidence_score: 84.85,
          confidence_factors: {
            raw_scores: { agent_agreement: 100, risk_score_factor: 75, volatility_factor: 78, sentiment_stability: 75, historical_accuracy: 69 },
            weighted_contributions: { agent_agreement: 40.0, risk_score_factor: 15.0, volatility_factor: 11.7, sentiment_stability: 11.25, historical_accuracy: 6.9 }
          },
          position_size: { percentage_of_portfolio: 12.0, quantity: 0.2758, entry_price: 43500.0, target_price: 46500.0, stop_loss: 41800.0 },
          reasoning: "The committee reached a unanimous agreement to BUY BTC. Positive ETF inflows support technical breakout signals. Low risk volatility allows high positioning.",
          key_factors: ["Unanimous consensus", "ETF inflows breakout", "Low risk profile"]
        },
        trade_result: { status: "completed", entry_price: 43500.0, quantity: 0.2758, exit_price: 46500.0, exit_timestamp: "2026-06-11T14:30:00Z", realized_pnl: 827.40, notes: "Target hit. Exited automatically at target." }
      });
    } else {
      applyTimelineData({
        symbol: "ETH",
        market_state: { symbol: "ETH", current_price: 2800.0, price_24h_high: 2950.0, price_24h_low: 2600.0, volume_24h: 450000000.0, volatility: 0.55, trend_direction: "DOWN", market_news_count: 25, market_conditions: "volatile" },
        initial_opinions: {
          technical_analyst: { recommendation: "BUY", confidence: 60, reasoning: "Aggressive oversold bounce support at $2,800. Fast reversal likely." },
          news_analyst: { recommendation: "HOLD", confidence: 70, reasoning: "High fear surrounding a major smart contract exploit report." },
          quant_analyst: { recommendation: "HOLD", confidence: 60, reasoning: "Model reports low probability of bounce success due to high drawdown speed." }
        },
        debate_transcript: [
          { agent_id: "technical_analyst", agent_name: "Technical Analyst", message_type: "ANALYSIS", content: "Initial Analysis: BUY. Oversold support indicates bounce potential.", confidence: 0.60, recommendation: "BUY" },
          { agent_id: "news_analyst", agent_name: "News Analyst", message_type: "CHALLENGE", content: "I challenge Technical Analyst. We are dealing with an active exploit report; buying now is highly speculative.", confidence: 0.70, recommendation: "HOLD" },
          { agent_id: "technical_analyst", agent_name: "Technical Analyst", message_type: "REVISION", content: "Given the exploit detail, I will revise my recommendation to HOLD until contract integrity is verified.", confidence: 0.70, recommendation: "HOLD" }
        ],
        voting_tally: {
          votes: {
            technical_analyst: { vote: "HOLD", weight: 1.2, confidence: 70 },
            quant_analyst: { vote: "HOLD", weight: 1.1, confidence: 60 },
            news_analyst: { vote: "HOLD", weight: 1.0, confidence: 70 }
          },
          proposed_action: "HOLD"
        },
        veto_verification: { risk_score: 85.0, risk_level: "critical", position_size_recommendation: 0.0, max_position_allowed: 0.0, approved: false, veto_reason: "VETO: Volatility is 0.55 and risk score is 85/100, which exceeds maximum drawdown limits. Exploits present systemic risk." },
        execution_decision: {
          action: "HOLD",
          confidence_score: 62.65,
          confidence_factors: {
            raw_scores: { agent_agreement: 100, risk_score_factor: 15, volatility_factor: 45, sentiment_stability: 40, historical_accuracy: 69 },
            weighted_contributions: { agent_agreement: 40.0, risk_score_factor: 3.0, volatility_factor: 6.75, sentiment_stability: 6.0, historical_accuracy: 6.9 }
          },
          position_size: { percentage_of_portfolio: 0.0, quantity: 0.0, entry_price: 2800.0, target_price: null, stop_loss: null },
          reasoning: "The trade proposal was rejected due to a Risk Manager VETO. The committee agreed on HOLD. Smart contract exploit reports and 55% volatility create critical downside risk.",
          key_factors: ["Risk Manager VETO", "Exploit risk", "High market volatility"]
        },
        trade_result: { status: "failed", entry_price: 2800.0, quantity: 0.0, exit_price: null, exit_timestamp: null, realized_pnl: 0.0, notes: "VETOED by Risk Manager. No execution occurred." }
      });
    }
  }

  function applyTimelineData(t: any) {
    setSelectedAsset(t.symbol as "BUY" | "SELL" | "HOLD" extends any ? any : any);
    setMarketState(t.market_state);
    setInitialOpinions(t.initial_opinions);
    setVotingTally(t.voting_tally);
    setVetoVerification(t.veto_verification);
    setExecutionDecision(t.execution_decision);
    setTradeResult(t.trade_result);
    
    // Setup debate player
    setFullTranscript(t.debate_transcript);
    setDebateTranscript(t.debate_transcript);
    setPlayIndex(t.debate_transcript.length);
    setIsPlaying(false);
  }

  // --- REPLAY CONTROLS PLAYER ---
  useEffect(() => {
    let interval: any;
    if (isPlaying && playIndex < fullTranscript.length) {
      interval = setInterval(() => {
        setDebateTranscript(prev => [...prev, fullTranscript[playIndex]]);
        setPlayIndex(idx => idx + 1);
      }, 1800);
    } else if (playIndex >= fullTranscript.length) {
      setIsPlaying(false);
    }
    return () => clearInterval(interval);
  }, [isPlaying, playIndex, fullTranscript]);

  const handleRestartReplay = () => {
    setDebateTranscript([]);
    setPlayIndex(0);
    setIsPlaying(true);
  };

  // --- SIMULATION (DEMO MODE) ENGINE ---
  const triggerSimulation = async (scenario: "crash" | "rally") => {
    if (isSimulating) return;
    setIsSimulating(true);
    setSimulationStep(1);
    
    const catalystName = scenario === "rally" ? "Bitcoin Spot ETF Approval" : "Ether Smart Contract Exploit";
    setSimulationLogs([
      `[CATALYST]: Injected market catalyst: ${catalystName}`,
      `[SYSTEM]: Dispatching session run request to FastAPI /api/replay/demo/run...`,
      `[ENGINE]: Triggering committee consensus graph...`
    ]);
    
    // Clear debate transcript in preparation for replay animation
    setDebateTranscript([]);
    setIsPlaying(false);
    
    try {
      setSimulationStep(2);
      const res = await fetch(`${BACKEND_URL}/api/replay/demo/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario })
      });
      
      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }
      
      const data = await res.json();
      const newSessionId = data.session_id;
      
      setSimulationStep(4);
      setSimulationLogs(prev => [
        ...prev,
        `[SUCCESS]: Agent debate run complete. Session ID: ${newSessionId}`,
        `[SYSTEM]: Synchronizing replay directories and loading timeline...`
      ]);
      
      // Load the timeline data
      await loadTimeline(newSessionId);
      
      // Re-fetch list to show the new item
      const listRes = await fetch(`${BACKEND_URL}/api/replay`);
      if (listRes.ok) {
        const listData = await listRes.json();
        setReplays(listData);
      }
      
      setSimulationStep(6);
      setSimulationLogs(prev => [
        ...prev,
        `[PLAYBACK]: Starting sequential debate playback animation. Enjoy the show!`
      ]);
      
      // Start sequential play anim
      setDebateTranscript([]);
      setPlayIndex(0);
      setIsPlaying(true);
      
      setSimulationStep(8);
    } catch (err) {
      console.error("Simulation trigger failed, falling back to local simulation", err);
      runLocalSimulationFallback(scenario);
    } finally {
      setIsSimulating(false);
    }
  };

  const runLocalSimulationFallback = (scenario: "crash" | "rally") => {
    // High-fidelity local simulation if API is offline
    const logs = scenario === "crash" 
      ? [
          "SEC announces potential delay of institutional spot Ether ETFs.",
          "Whale wallets detected transferring over $250M of ETH to exchanges, signaling sell pressure.",
          "Committee session initiated by Execution Chairman.",
          "Market volatility surges to 0.48. Risk indexes spiking.",
          "Debate Round 2: Tech challenged by News Analyst.",
          "Debate Round 2 Complete. Consensus calculated.",
          "Voting tallies finalized. Querying Risk Manager Gatekeeper...",
          "Risk assessment concluded. Execution Agent synthesizing final decision...",
          "Session complete. Appending results to trade ledger."
        ]
      : [
          "SEC officially approves spot Bitcoin ETF listings on all major exchanges.",
          "Bitcoin net inflows surge by $500M in the first hour of trading.",
          "Committee session initiated by Execution Chairman.",
          "Market volatility at stable 0.20. Bullish momentum active.",
          "Debate Round 2: News agrees with Quant Analyst.",
          "Debate Round 2 Complete. Consensus calculated.",
          "Voting tallies finalized. Querying Risk Manager Gatekeeper...",
          "Risk assessment concluded. Execution Agent synthesizing final decision...",
          "Session complete. Appending results to trade ledger."
        ];
        
    setSimulationLogs([logs[0]]);
    
    setMarketState({
      symbol: scenario === "crash" ? "ETH" : "BTC",
      current_price: scenario === "crash" ? 3100.0 : 42000.0,
      price_24h_high: scenario === "crash" ? 3350.0 : 42500.0,
      price_24h_low: scenario === "crash" ? 3050.0 : 40800.0,
      volume_24h: scenario === "crash" ? 98000000.0 : 150000000.0,
      volatility: scenario === "crash" ? 0.48 : 0.20,
      trend_direction: scenario === "crash" ? "DOWN" : "UP",
      market_news_count: 18,
      market_conditions: scenario === "crash" ? "volatile" : "bullish",
    });
    
    let step = 0;
    const interval = setInterval(() => {
      step++;
      setSimulationStep(step);
      
      if (step === 1) {
        setSimulationLogs(prev => [...prev, logs[1]]);
        const techMsg: AgentMessage = scenario === "crash"
          ? { agent_id: "technical_analyst", agent_name: "Technical Analyst", message_type: "ANALYSIS", content: "Initial Analysis: BUY. RSI is oversold at 28, indicating bounce potential near support $3,050.", confidence: 0.65, recommendation: "BUY" }
          : { agent_id: "technical_analyst", agent_name: "Technical Analyst", message_type: "ANALYSIS", content: "Initial Analysis: BUY. Strong trend confirmation above EMA-50 and EMA-200. Golden cross on 4h.", confidence: 0.85, recommendation: "BUY" };
        setDebateTranscript([techMsg]);
        setInitialOpinions(prev => ({ ...prev, technical_analyst: techMsg }));
      }
      else if (step === 2) {
        setSimulationLogs(prev => [...prev, logs[2]]);
        const newsMsg: AgentMessage = scenario === "crash"
          ? { agent_id: "news_analyst", agent_name: "News Analyst", message_type: "ANALYSIS", content: "Initial Analysis: HOLD. Regulatory ETF delays and $250M whale inflows to Coinbase create heavy selling bias.", confidence: 0.80, recommendation: "HOLD" }
          : { agent_id: "news_analyst", agent_name: "News Analyst", message_type: "ANALYSIS", content: "Initial Analysis: BUY. Institutional ETF approvals and record inflows create massive supply shock bullish sentiment.", confidence: 0.90, recommendation: "BUY" };
        setDebateTranscript(prev => [...prev, newsMsg]);
        setInitialOpinions(prev => ({ ...prev, news_analyst: newsMsg }));
      }
      else if (step === 3) {
        setSimulationLogs(prev => [...prev, logs[3]]);
        const quantMsg: AgentMessage = scenario === "crash"
          ? { agent_id: "quant_analyst", agent_name: "Quant Analyst", message_type: "ANALYSIS", content: "Initial Analysis: HOLD. Historical crash correlation analysis indicates momentum is negative, expected value falls to -0.12.", confidence: 0.70, recommendation: "HOLD" }
          : { agent_id: "quant_analyst", agent_name: "Quant Analyst", message_type: "ANALYSIS", content: "Initial Analysis: BUY. High probability momentum continuation. Statistics show 82% success rate, expected value +1.85.", confidence: 0.80, recommendation: "BUY" };
        setDebateTranscript(prev => [...prev, quantMsg]);
        setInitialOpinions(prev => ({ ...prev, quant_analyst: quantMsg }));
      }
      else if (step === 4) {
        setSimulationLogs(prev => [...prev, logs[4]]);
        if (scenario === "crash") {
          const newsChallenge: AgentMessage = { agent_id: "news_analyst", agent_name: "News Analyst", message_type: "CHALLENGE", content: "Replying to Technical Analyst. Buying oversold support ignores the fact that whales are dumping. Sentiment is negative.", confidence: 0.85, recommendation: "HOLD" };
          setDebateTranscript(prev => [...prev, newsChallenge]);
        } else {
          const newsAgree: AgentMessage = { agent_id: "news_analyst", agent_name: "News Analyst", message_type: "AGREEMENT", content: "I agree with Quant Analyst. ETF flows represent sticky capital, supporting positive momentum.", confidence: 0.95, recommendation: "BUY" };
          setDebateTranscript(prev => [...prev, newsAgree]);
        }
      }
      else if (step === 5) {
        setSimulationLogs(prev => [...prev, logs[5]]);
        if (scenario === "crash") {
          const techRevise: AgentMessage = { agent_id: "technical_analyst", agent_name: "Technical Analyst", message_type: "REVISION", content: "Given whale outflows and quant statistics, I revise my stance from BUY to HOLD. Protecting capital is priority.", confidence: 0.75, recommendation: "HOLD" };
          setDebateTranscript(prev => [...prev, techRevise]);
          setVotingTally({
            votes: {
              technical_analyst: { vote: "HOLD", weight: 1.2, confidence: 75 },
              quant_analyst: { vote: "HOLD", weight: 1.1, confidence: 70 },
              news_analyst: { vote: "HOLD", weight: 1.0, confidence: 80 }
            },
            proposed_action: "HOLD"
          });
        } else {
          const quantAgree: AgentMessage = { agent_id: "quant_analyst", agent_name: "Quant Analyst", message_type: "AGREEMENT", content: "Maintaining BUY. Standard deviation is low. Sentiment is extremely stable.", confidence: 0.85, recommendation: "BUY" };
          setDebateTranscript(prev => [...prev, quantAgree]);
          setVotingTally({
            votes: {
              technical_analyst: { vote: "BUY", weight: 1.2, confidence: 85 },
              quant_analyst: { vote: "BUY", weight: 1.1, confidence: 80 },
              news_analyst: { vote: "BUY", weight: 1.0, confidence: 90 }
            },
            proposed_action: "BUY"
          });
        }
      }
      else if (step === 6) {
        setSimulationLogs(prev => [...prev, logs[6]]);
        if (scenario === "crash") {
          setVetoVerification({
            risk_score: 82.0,
            risk_level: "critical",
            position_size_recommendation: 0.0,
            max_position_allowed: 0.0,
            approved: false,
            veto_reason: "VETO: Portfolio drawdown limits breached. High volatility (0.48) and whale selling create excessive loss risk."
          });
        } else {
          setVetoVerification({
            risk_score: 18.0,
            risk_level: "low",
            position_size_recommendation: 20000.0,
            max_position_allowed: 0.20,
            approved: true,
            veto_reason: "Approved: Risk metrics are highly favorable. Max sizing of 20% allowed."
          });
        }
      }
      else if (step === 7) {
        setSimulationLogs(prev => [...prev, logs[7]]);
        if (scenario === "crash") {
          setExecutionDecision({
            action: "HOLD",
            confidence_score: 64.30,
            confidence_factors: {
              raw_scores: { agent_agreement: 100, risk_score_factor: 18, volatility_factor: 52, sentiment_stability: 42, historical_accuracy: 69 },
              weighted_contributions: { agent_agreement: 40.0, risk_score_factor: 3.6, volatility_factor: 7.8, sentiment_stability: 6.3, historical_accuracy: 6.9 }
            },
            position_size: { percentage_of_portfolio: 0.0, quantity: 0.0, entry_price: 3100.0, target_price: null, stop_loss: null },
            reasoning: "The committee reached a HOLD consensus due to the Risk VETO. Smart contract ETF delay rumors and whale exchange inflows present excessive downside risks.",
            key_factors: ["Risk Manager VETO", "Whale selling inflows", "High volatility metrics"]
          });
          setTradeResult({
            status: "failed",
            entry_price: 3100.0,
            quantity: 0.0,
            exit_price: null,
            exit_timestamp: null,
            realized_pnl: 0.0,
            notes: "VETOED by Risk Manager. No execution occurred."
          });
        } else {
          setExecutionDecision({
            action: "BUY",
            confidence_score: 91.25,
            confidence_factors: {
              raw_scores: { agent_agreement: 100, risk_score_factor: 82, volatility_factor: 80, sentiment_stability: 90, historical_accuracy: 69 },
              weighted_contributions: { agent_agreement: 40.0, risk_score_factor: 16.4, volatility_factor: 12.0, sentiment_stability: 13.5, historical_accuracy: 6.9 }
            },
            position_size: { percentage_of_portfolio: 16.0, quantity: 0.7619, entry_price: 42000.0, target_price: 45500.0, stop_loss: 40500.0 },
            reasoning: "The committee reached a unanimous BUY decision. Structural institutional ETF demand creates a breakout setup. Low risk score authorizes a large position size.",
            key_factors: ["Spot ETF approval", "Unanimous committee consensus", "High sentiment stability", "Low risk profile"]
          });
          setTradeResult({
            status: "executed",
            entry_price: 42000.0,
            quantity: 0.7619,
            exit_price: null,
            exit_timestamp: null,
            realized_pnl: 0.0,
            notes: "Order executed at $42,000. Pending target $45,500."
          });
        }
      }
      else if (step === 8) {
        setSimulationLogs(prev => [...prev, logs[8]]);
        setIsSimulating(false);
        clearInterval(interval);
      }
    }, 1500);
  };

  // Simulate Exit Price update during a live simulation order
  const handleSimulateExit = async () => {
    if (executionDecision.action === "BUY" && tradeResult.status === "executed") {
      const exitPrice = executionDecision.position_size.target_price || 45500.0;
      
      if (activeSessionId) {
        try {
          // Sync with the backend mock completion
          const res = await fetch(`${BACKEND_URL}/api/replay/${activeSessionId}/mock-complete`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ exit_price: exitPrice })
          });
          
          if (res.ok) {
            // Reload from backend
            await loadTimeline(activeSessionId);
            // Refresh sidebar list
            const listRes = await fetch(`${BACKEND_URL}/api/replay`);
            if (listRes.ok) {
              const listData = await listRes.json();
              setReplays(listData);
            }
            return;
          }
        } catch (err) {
          console.error("Failed to complete trade on backend, doing local complete", err);
        }
      }

      // Local fallback in case of connection error or offline
      const entry = tradeResult.entry_price;
      const qty = tradeResult.quantity;
      const pnl = (exitPrice - entry) * qty;
      setTradeResult({
        status: "completed",
        entry_price: entry,
        quantity: qty,
        exit_price: exitPrice,
        exit_timestamp: new Date().toISOString(),
        realized_pnl: round(pnl, 2),
        notes: `Target $${exitPrice.toLocaleString()} hit in live simulation breakout.`
      });
      setReplays(prev => [
        {
          session_id: activeSessionId || "simulated-active-run",
          symbol: marketState.symbol,
          final_action: "BUY",
          confidence_score: executionDecision.confidence_score,
          trade_status: "completed",
          realized_pnl: pnl,
          created_at: new Date().toISOString()
        },
        ...prev.filter(r => r.session_id !== activeSessionId)
      ]);
    }
  };

  function round(val: number, decimals: number) {
    return Math.round(val * Math.pow(10, decimals)) / Math.pow(10, decimals);
  }

  // Auto scroll debate
  useEffect(() => {
    debateEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [debateTranscript]);

  return (
    <div className="flex flex-col min-h-screen bg-primary text-foreground font-sans selection:bg-accent selection:text-primary">
      
      {/* --- HEADER --- */}
      <header className="flex items-center justify-between border-b border-border-terminal bg-[#0A0C0E] py-3.5 px-6 shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-accent animate-pulse-terminal"></span>
            <h1 className="text-lg font-mono font-bold tracking-widest text-[#FFF]">COUNCIL</h1>
          </div>
          <div className="hidden h-5 w-[1px] bg-border-terminal md:block"></div>
          <span className="hidden font-mono text-xs text-[#8F949E] tracking-wider md:inline">
            INSTITUTIONAL AI INVESTMENT COMMITTEE
          </span>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${apiStatus === "connected" ? "bg-success" : "bg-warning"}`}></span>
            <span className="font-mono text-xs text-[#8F949E]">
              {apiStatus === "connected" ? "API: 8000" : "API: OFFLINE BACKUP"}
            </span>
          </div>

          <div className="h-5 w-[1px] bg-border-terminal"></div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="font-mono text-[10px] leading-3 text-[#8F949E]">NAV VALUE</div>
              <div className="font-mono font-bold text-accent text-sm">$100,827.40</div>
            </div>
            <div className="text-right hidden sm:block">
              <div className="font-mono text-[10px] leading-3 text-[#8F949E]">WIN RATE</div>
              <div className="font-mono font-bold text-success text-sm">66.7%</div>
            </div>
          </div>
        </div>
      </header>

      {/* --- DASHBOARD GRID --- */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 p-4 min-h-0 overflow-y-auto">
        
        {/* --- LEFT COLUMN: Market & Portfolio (Span 3) --- */}
        <section className="lg:col-span-3 flex flex-col gap-4 min-h-0">
          
          {/* MARKET OVERVIEW */}
          <div className="border border-border-terminal bg-secondary p-4 flex flex-col gap-3 shrink-0">
            <div className="flex items-center justify-between border-b border-border-terminal pb-2">
              <span className="font-mono font-bold text-xs tracking-wider text-[#A8AEBA]">MARKET OVERVIEW</span>
              <div className="flex gap-1.5">
                <button 
                  onClick={() => setSelectedAsset("BTC")} 
                  className={`px-2 py-0.5 font-mono text-[10px] border transition-colors ${selectedAsset === "BTC" ? "border-accent text-accent bg-[#D4A24C]/[0.05]" : "border-border-terminal text-[#8F949E]"}`}
                >
                  BTC
                </button>
                <button 
                  onClick={() => setSelectedAsset("ETH")} 
                  className={`px-2 py-0.5 font-mono text-[10px] border transition-colors ${selectedAsset === "ETH" ? "border-accent text-accent bg-[#D4A24C]/[0.05]" : "border-border-terminal text-[#8F949E]"}`}
                >
                  ETH
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="font-mono text-[10px] text-[#8F949E]">SYMBOL</span>
                <div className="font-mono font-bold text-sm text-[#FFF]">{marketState.symbol}/USD</div>
              </div>
              <div className="text-right">
                <span className="font-mono text-[10px] text-[#8F949E]">PRICE</span>
                <div className="font-mono font-bold text-sm text-accent">${marketState.current_price.toLocaleString()}</div>
              </div>
              <div>
                <span className="font-mono text-[10px] text-[#8F949E]">VOLATILITY</span>
                <div className={`font-mono font-bold text-xs ${marketState.volatility > 0.40 ? "text-danger" : "text-success"}`}>
                  {(marketState.volatility * 100).toFixed(0)}% ({marketState.market_conditions.toUpperCase()})
                </div>
              </div>
              <div className="text-right">
                <span className="font-mono text-[10px] text-[#8F949E]">24H TREND</span>
                <div className={`font-mono font-bold text-xs ${marketState.trend_direction === "UP" ? "text-success" : "text-danger"}`}>
                  {marketState.trend_direction === "UP" ? "▲ BULLISH" : "▼ BEARISH"}
                </div>
              </div>
            </div>

            {/* High-Fidelity SVG Candle Ticker Chart */}
            <div className="h-32 border border-border-terminal bg-primary relative mt-1 overflow-hidden">
              <svg className="w-full h-full p-2" viewBox="0 0 100 50" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="chart-glow" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#D4A24C" stopOpacity="0.15" />
                    <stop offset="100%" stopColor="#D4A24C" stopOpacity="0" />
                  </linearGradient>
                </defs>
                {/* SVG candles grid */}
                <line x1="0" y1="25" x2="100" y2="25" stroke="#1B1F24" strokeWidth="0.5" />
                <line x1="0" y1="12" x2="100" y2="12" stroke="#1B1F24" strokeWidth="0.5" />
                <line x1="0" y1="38" x2="100" y2="38" stroke="#1B1F24" strokeWidth="0.5" />
                
                {/* Simulated Candle sticks */}
                {selectedAsset === "BTC" ? (
                  // Up candles for BTC
                  <g>
                    <line x1="10" y1="30" x2="10" y2="45" stroke="#1D9B72" strokeWidth="0.5" />
                    <rect x="8" y="33" width="4" height="8" fill="#1D9B72" />
                    
                    <line x1="30" y1="20" x2="30" y2="38" stroke="#1D9B72" strokeWidth="0.5" />
                    <rect x="28" y="23" width="4" height="11" fill="#1D9B72" />

                    <line x1="50" y1="15" x2="50" y2="28" stroke="#A84747" strokeWidth="0.5" />
                    <rect x="48" y="17" width="4" height="8" fill="#A84747" />

                    <line x1="70" y1="10" x2="70" y2="22" stroke="#1D9B72" strokeWidth="0.5" />
                    <rect x="68" y="12" width="4" height="8" fill="#1D9B72" />

                    <line x1="90" y1="5" x2="90" y2="15" stroke="#1D9B72" strokeWidth="0.5" />
                    <rect x="88" y="6" width="4" height="7" fill="#1D9B72" />
                  </g>
                ) : (
                  // Volatile/down candles for ETH
                  <g>
                    <line x1="10" y1="10" x2="10" y2="25" stroke="#A84747" strokeWidth="0.5" />
                    <rect x="8" y="12" width="4" height="10" fill="#A84747" />

                    <line x1="30" y1="18" x2="30" y2="35" stroke="#1D9B72" strokeWidth="0.5" />
                    <rect x="28" y="21" width="4" height="8" fill="#1D9B72" />

                    <line x1="50" y1="25" x2="50" y2="45" stroke="#A84747" strokeWidth="0.5" />
                    <rect x="48" y="28" width="4" height="13" fill="#A84747" />

                    <line x1="70" y1="35" x2="70" y2="48" stroke="#A84747" strokeWidth="0.5" />
                    <rect x="68" y="38" width="4" height="7" fill="#A84747" />

                    <line x1="90" y1="30" x2="90" y2="40" stroke="#1D9B72" strokeWidth="0.5" />
                    <rect x="88" y="32" width="4" height="6" fill="#1D9B72" />
                  </g>
                )}
              </svg>
              <div className="absolute bottom-1 right-2 font-mono text-[9px] text-[#8F949E]">INTERVAL: 1H</div>
            </div>
          </div>

          {/* PORTFOLIO POSITION PANEL */}
          <div className="border border-border-terminal bg-secondary p-4 flex-1 flex flex-col gap-3 min-h-0">
            <div className="border-b border-border-terminal pb-2 flex justify-between items-center">
              <span className="font-mono font-bold text-xs tracking-wider text-[#A8AEBA]">PORTFOLIO SUMMARY</span>
              <span className="font-mono text-[9px] bg-success/[0.1] text-success px-1.5 py-0.5 border border-success/20">LIVE STATUS</span>
            </div>

            <div className="grid grid-cols-2 gap-3 shrink-0 text-xs">
              <div>
                <span className="font-mono text-[10px] text-[#8F949E]">INITIAL CAPITAL</span>
                <div className="font-mono font-bold text-[#FFF]">$100,000.00</div>
              </div>
              <div className="text-right">
                <span className="font-mono text-[10px] text-[#8F949E]">UNREALIZED P&L</span>
                <div className={`font-mono font-bold ${tradeResult.status === "executed" ? "text-success animate-pulse-terminal" : "text-[#FFF]"}`}>
                  {tradeResult.status === "executed" ? "+$1,980.00" : "$0.00"}
                </div>
              </div>
              <div>
                <span className="font-mono text-[10px] text-[#8F949E]">WIN RATE</span>
                <div className="font-mono font-bold text-success">66.7%</div>
              </div>
              <div className="text-right">
                <span className="font-mono text-[10px] text-[#8F949E]">TOTAL SESSIONS</span>
                <div className="font-mono font-bold text-[#FFF]">3</div>
              </div>
            </div>

            {/* Current Open Positions list */}
            <div className="flex-1 flex flex-col gap-2 min-h-0 overflow-y-auto mt-2">
              <span className="font-mono text-[10px] text-[#8F949E] border-b border-border-terminal pb-1">ACTIVE LEDGER ORDER</span>
              {tradeResult.status === "executed" ? (
                <div className="border border-accent/20 bg-primary/40 p-2.5 flex flex-col gap-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-mono font-bold text-accent">BUY {marketState.symbol} POSITION</span>
                    <span className="font-mono text-[9px] text-success bg-success/[0.1] px-1 border border-success/20">EXECUTED</span>
                  </div>
                  <div className="grid grid-cols-2 gap-y-1 gap-x-2 text-[10px] font-mono text-[#8F949E]">
                    <span>Quantity:</span>
                    <span className="text-[#FFF] text-right">{tradeResult.quantity} {marketState.symbol}</span>
                    <span>Entry Price:</span>
                    <span className="text-[#FFF] text-right">${tradeResult.entry_price.toLocaleString()}</span>
                    <span>Target Price:</span>
                    <span className="text-success text-right">${executionDecision.position_size.target_price?.toLocaleString()}</span>
                    <span>Stop Loss:</span>
                    <span className="text-danger text-right">${executionDecision.position_size.stop_loss?.toLocaleString()}</span>
                  </div>
                  {/* Hackathon Exit simulation trigger */}
                  <button 
                    onClick={handleSimulateExit}
                    className="w-full mt-1.5 py-1 text-center font-mono text-[9px] font-bold tracking-wider text-primary bg-accent hover:bg-accent/90 transition-colors uppercase cursor-pointer"
                  >
                    Simulate Target Hit (Exit Order)
                  </button>
                </div>
              ) : tradeResult.status === "completed" && tradeResult.realized_pnl > 0 ? (
                <div className="border border-success/20 bg-success/[0.03] p-2.5 flex flex-col gap-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-mono font-bold text-success">BUY {marketState.symbol} EXITED</span>
                    <span className="font-mono text-[9px] text-success font-bold">+${tradeResult.realized_pnl.toFixed(2)} P&L</span>
                  </div>
                  <p className="font-mono text-[10px] text-[#8F949E] leading-4 mt-1">
                    {tradeResult.notes}
                  </p>
                </div>
              ) : (
                <div className="flex-1 flex items-center justify-center border border-dashed border-border-terminal p-4 text-center">
                  <span className="font-mono text-[10px] text-[#8F949E]">No active order. Committee in hold or veto session.</span>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* --- CENTER COLUMN: Debate Chamber & Votes (Span 6) --- */}
        <section className="lg:col-span-6 flex flex-col gap-4 min-h-0">
          
          {/* DEBATE CHAMBER PANEL */}
          <div className="border border-border-terminal bg-[#0A0C0E] flex-1 flex flex-col min-h-0 relative">
            
            {/* Chamber Header & Controls */}
            <div className="flex items-center justify-between border-b border-border-terminal bg-secondary py-2 px-4">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-success"></span>
                <span className="font-mono font-bold text-xs tracking-wider text-[#A8AEBA]">COMMITTEE CHAMBER</span>
              </div>
              
              {/* Playback controller */}
              <div className="flex items-center gap-3">
                {isSimulating ? (
                  <span className="font-mono text-[10px] text-accent animate-pulse-terminal uppercase tracking-widest font-bold">
                    Running Live Simulation Turn...
                  </span>
                ) : (
                  <div className="flex items-center gap-1.5">
                    <button 
                      onClick={handleRestartReplay}
                      disabled={isPlaying}
                      className="px-2 py-0.5 border border-border-terminal font-mono text-[9px] text-[#A8AEBA] hover:text-[#FFF] hover:border-[#FFF] disabled:opacity-40 transition-colors uppercase cursor-pointer"
                    >
                      Replay Debate
                    </button>
                    <button 
                      onClick={() => setIsPlaying(!isPlaying)}
                      className="px-2 py-0.5 border border-border-terminal font-mono text-[9px] text-accent hover:text-[#FFF] hover:border-accent transition-colors uppercase cursor-pointer"
                    >
                      {isPlaying ? "Pause" : "Play"}
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Chat speech bubbles viewport */}
            <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-4 min-h-0 font-mono text-xs leading-5">
              
              {/* System Session Start message */}
              <div className="border border-border-terminal bg-secondary/30 py-2.5 px-3.5 text-[#8F949E] text-[11px] leading-4 border-l-2 border-l-accent">
                [SYSTEM]: Initializing committee debate session for asset {marketState.symbol}. Volatility standard: {marketState.volatility}. Expected max rounds: 3.
              </div>

              {/* Debate Speech bubbles list */}
              {debateTranscript.map((msg, index) => {
                const isTech = msg.agent_id.includes("technical");
                const isNews = msg.agent_id.includes("news");
                const isQuant = msg.agent_id.includes("quant");
                
                // Color coding borders for speech bubbles based on type
                let borderStyle = "border-border-terminal";
                let badgeStyle = "bg-[#8F949E]/10 text-[#8F949E]";
                if (msg.message_type === "CHALLENGE") {
                  borderStyle = "border-danger/30 border-l-2 border-l-danger bg-danger/[0.01]";
                  badgeStyle = "bg-danger/10 text-danger border border-danger/20";
                } else if (msg.message_type === "AGREEMENT") {
                  borderStyle = "border-success/30 border-l-2 border-l-success bg-success/[0.01]";
                  badgeStyle = "bg-success/10 text-success border border-success/20";
                } else if (msg.message_type === "REVISION") {
                  borderStyle = "border-accent/40 border-l-2 border-l-accent bg-accent/[0.01]";
                  badgeStyle = "bg-accent/15 text-accent border border-accent/30";
                }

                return (
                  <div key={index} className={`flex flex-col border p-3 ${borderStyle}`}>
                    <div className="flex items-center justify-between border-b border-border-terminal/40 pb-1.5 mb-2">
                      <div className="flex items-center gap-2 font-bold text-xs text-[#FFF]">
                        <span className={`h-1.5 w-1.5 rounded-full ${isTech ? "bg-accent" : isNews ? "bg-success" : "bg-purple-400"}`}></span>
                        {msg.agent_name}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-[9px] px-1.5 py-0.2 uppercase font-semibold ${badgeStyle}`}>
                          {msg.message_type}
                        </span>
                        <span className="text-[10px] text-[#8F949E]">
                          Rec: <strong className={msg.recommendation === "BUY" ? "text-success" : msg.recommendation === "SELL" ? "text-danger" : "text-accent"}>{msg.recommendation}</strong>
                        </span>
                      </div>
                    </div>
                    <p className="text-[#DFE1E5] leading-5 text-[11px] font-mono">
                      {msg.content}
                    </p>
                  </div>
                );
              })}

              {/* Loader during playback */}
              {isPlaying && playIndex < fullTranscript.length && (
                <div className="flex items-center gap-2 text-[#8F949E] italic text-[11px] animate-pulse-terminal">
                  <span className="h-1.5 w-1.5 bg-[#8F949E] rounded-full animate-bounce"></span>
                  Analyst typing response...
                </div>
              )}

              {/* End pointer */}
              <div ref={debateEndRef}></div>
            </div>

            {/* Simulation live log logs console at bottom */}
            {isSimulating && (
              <div className="border-t border-border-terminal bg-[#0A0C0E] py-2 px-4 shrink-0 font-mono text-[10px]">
                <div className="flex justify-between items-center text-[#8F949E] border-b border-border-terminal pb-1 mb-1">
                  <span>SIMULATION STATUS CONSOLE</span>
                  <span className="animate-pulse-terminal text-accent">STEP {simulationStep}/8</span>
                </div>
                <div className="max-h-16 overflow-y-auto flex flex-col gap-0.5 text-success">
                  {simulationLogs.map((log, idx) => (
                    <div key={idx}>&gt; {log}</div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* COMMITTEE VOTES & MAJORITY TALLY PANEL */}
          <div className="border border-border-terminal bg-secondary p-4 shrink-0 flex flex-col gap-3">
            <span className="font-mono font-bold text-xs tracking-wider text-[#A8AEBA] border-b border-border-terminal pb-2">VOTING TALLY & WEIGHTS</span>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-1">
              {Object.entries(votingTally.votes).map(([agentId, data]: [string, any], idx) => {
                const name = agentId === "technical_analyst" ? "Technical" : agentId === "quant_analyst" ? "Quant" : "News";
                return (
                  <div key={idx} className="border border-border-terminal p-2.5 flex flex-col gap-1.5 bg-primary/20">
                    <div className="flex justify-between items-center">
                      <span className="font-mono font-bold text-[10px] text-[#FFF]">{name} Analyst</span>
                      <span className="font-mono text-[9px] text-[#8F949E]">Weight: {data.weight}x</span>
                    </div>
                    <div className="flex justify-between items-end">
                      <div className="font-mono text-[10px] text-[#8F949E]">
                        Vote: <strong className={data.vote === "BUY" ? "text-success" : data.vote === "SELL" ? "text-danger" : "text-accent"}>{data.vote}</strong>
                      </div>
                      <div className="font-mono text-[10px] text-[#FFF]">{data.confidence}% conf</div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            <div className="flex items-center justify-between border border-border-terminal bg-primary py-2 px-3 mt-1 text-xs">
              <span className="font-mono font-bold text-[#8F949E]">COMMITTEE PROPOSED ACTION:</span>
              <div className="font-mono font-bold text-sm tracking-wider">
                <span className={votingTally.proposed_action === "BUY" ? "text-success" : votingTally.proposed_action === "SELL" ? "text-danger" : "text-accent"}>
                  {votingTally.proposed_action}
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* --- RIGHT COLUMN: Score radial & listings (Span 3) --- */}
        <section className="lg:col-span-3 flex flex-col gap-4 min-h-0">
          
          {/* CONFIDENCE RADIAL METER & FACTORS BREAKDOWN */}
          <div className="border border-border-terminal bg-secondary p-4 shrink-0 flex flex-col gap-3">
            <span className="font-mono font-bold text-xs tracking-wider text-[#A8AEBA] border-b border-border-terminal pb-2">CONFIDENCE GAUGE</span>
            
            {/* Radial score circle */}
            <div className="flex items-center justify-center gap-4 py-2 border-b border-border-terminal/40">
              <div className="relative h-20 w-20 flex items-center justify-center shrink-0">
                <svg className="absolute w-full h-full transform -rotate-90">
                  <circle cx="40" cy="40" r="34" stroke="#1B1F24" strokeWidth="4.5" fill="transparent" />
                  <circle 
                    cx="40" 
                    cy="40" 
                    r="34" 
                    stroke="#D4A24C" 
                    strokeWidth="4.5" 
                    fill="transparent" 
                    strokeDasharray={2 * Math.PI * 34}
                    strokeDashoffset={2 * Math.PI * 34 * (1 - executionDecision.confidence_score / 100)}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="font-mono text-center">
                  <span className="text-sm font-bold text-[#FFF]">{executionDecision.confidence_score.toFixed(0)}</span>
                  <span className="text-[10px] text-[#8F949E] block leading-none">%</span>
                </div>
              </div>
              
              <div className="font-mono text-xs leading-4">
                <span className="text-[10px] text-[#8F949E]">EXECUTIVE SUMMARY</span>
                <p className="text-[11px] text-[#DFE1E5] mt-1 line-clamp-3">
                  {executionDecision.reasoning}
                </p>
              </div>
            </div>

            {/* Explainable Factor checklist */}
            <div className="flex flex-col gap-1.5 font-mono text-[10px] leading-3 text-[#8F949E] mt-1.5">
              <div className="flex justify-between items-center">
                <span>1. Agent Agreement (40%)</span>
                <span className="text-[#FFF]">{executionDecision.confidence_factors.weighted_contributions.agent_agreement.toFixed(1)}% ({executionDecision.confidence_factors.raw_scores.agent_agreement}%)</span>
              </div>
              <div className="flex justify-between items-center">
                <span>2. Risk Level (20%)</span>
                <span className="text-[#FFF]">{executionDecision.confidence_factors.weighted_contributions.risk_score_factor.toFixed(1)}% ({executionDecision.confidence_factors.raw_scores.risk_score_factor}%)</span>
              </div>
              <div className="flex justify-between items-center">
                <span>3. Market Volatility (15%)</span>
                <span className="text-[#FFF]">{executionDecision.confidence_factors.weighted_contributions.volatility_factor.toFixed(1)}% ({executionDecision.confidence_factors.raw_scores.volatility_factor}%)</span>
              </div>
              <div className="flex justify-between items-center">
                <span>4. Sentiment Stability (15%)</span>
                <span className="text-[#FFF]">{executionDecision.confidence_factors.weighted_contributions.sentiment_stability.toFixed(1)}% ({executionDecision.confidence_factors.raw_scores.sentiment_stability}%)</span>
              </div>
              <div className="flex justify-between items-center">
                <span>5. Agent Accuracies (10%)</span>
                <span className="text-[#FFF]">{executionDecision.confidence_factors.weighted_contributions.historical_accuracy.toFixed(1)}% ({executionDecision.confidence_factors.raw_scores.historical_accuracy}%)</span>
              </div>
            </div>
          </div>

          {/* COMMITTEE AGENT STATUS DIRECTORY */}
          <div className="border border-border-terminal bg-secondary p-4 shrink-0 flex flex-col gap-2.5">
            <span className="font-mono font-bold text-xs tracking-wider text-[#A8AEBA] border-b border-border-terminal pb-2">AGENT PANEL</span>
            <div className="flex flex-col gap-2 max-h-48 overflow-y-auto">
              {[
                { name: "Technical Analyst", status: "ACTIVE", accuracy: 72 },
                { name: "News Analyst", status: "ACTIVE", accuracy: 65 },
                { name: "Quant Analyst", status: "ACTIVE", accuracy: 70 },
                { name: "Risk Manager", status: "ACTIVE (GATE)", accuracy: 92 },
                { name: "Execution Agent", status: "ACTIVE (SYNTH)", accuracy: 88 }
              ].map((agent, index) => (
                <div key={index} className="flex items-center justify-between border border-border-terminal bg-primary/20 p-2 font-mono text-[10px]">
                  <div className="flex flex-col">
                    <span className="font-bold text-[#FFF]">{agent.name}</span>
                    <span className="text-[9px] text-[#8F949E]">Accuracy: {agent.accuracy}%</span>
                  </div>
                  <span className="px-1.5 py-0.5 border border-success/20 bg-success/[0.05] text-success text-[9px]">
                    {agent.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* TABS PANEL: REPLAYS, TRADE JOURNAL, DEMO (Flex-1) */}
          <div className="border border-border-terminal bg-secondary flex-1 flex flex-col min-h-0">
            {/* Tabs selector */}
            <div className="flex border-b border-border-terminal bg-[#0A0C0E] shrink-0 font-mono text-[10px]">
              <button 
                onClick={() => setActiveRightTab("replay")}
                className={`flex-1 text-center py-2 border-r border-border-terminal uppercase cursor-pointer ${activeRightTab === "replay" ? "text-accent bg-secondary font-bold" : "text-[#8F949E] hover:text-[#FFF]"}`}
              >
                Replays
              </button>
              <button 
                onClick={() => setActiveRightTab("journal")}
                className={`flex-1 text-center py-2 border-r border-border-terminal uppercase cursor-pointer ${activeRightTab === "journal" ? "text-accent bg-secondary font-bold" : "text-[#8F949E] hover:text-[#FFF]"}`}
              >
                Journal
              </button>
              <button 
                onClick={() => setActiveRightTab("demo")}
                className={`flex-1 text-center py-2 uppercase cursor-pointer ${activeRightTab === "demo" ? "text-accent bg-secondary font-bold" : "text-[#8F949E] hover:text-[#FFF]"}`}
              >
                Demo
              </button>
            </div>

            {/* Tab content viewer */}
            <div className="flex-1 p-3 overflow-y-auto min-h-0">
              
              {/* TAB 1: REPLAY HISTORY */}
              {activeRightTab === "replay" && (
                <div className="flex flex-col gap-2.5">
                  {replays.map((rep, idx) => (
                    <div 
                      key={idx}
                      onClick={() => loadTimeline(rep.session_id)}
                      className={`border p-2.5 flex flex-col gap-1.5 transition-colors cursor-pointer ${activeSessionId === rep.session_id ? "border-accent bg-[#D4A24C]/[0.03]" : "border-border-terminal bg-primary/20 hover:border-[#8F949E]"}`}
                    >
                      <div className="flex justify-between items-center text-xs font-mono">
                        <span className="font-bold text-[#FFF]">{rep.symbol}/USD Session</span>
                        <span className={rep.final_action === "BUY" ? "text-success font-bold" : rep.final_action === "SELL" ? "text-danger font-bold" : "text-accent font-bold"}>
                          {rep.final_action}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-[10px] font-mono text-[#8F949E]">
                        <span>Conf: {rep.confidence_score.toFixed(0)}%</span>
                        <span>
                          {rep.realized_pnl !== undefined && rep.realized_pnl !== null 
                            ? `PNL: $${rep.realized_pnl.toFixed(2)}` 
                            : "Vetoed/No Execution"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* TAB 2: TRADE JOURNAL LESSONS */}
              {activeRightTab === "journal" && (
                <div className="flex flex-col gap-3 font-mono text-[10px] leading-4">
                  <div className="border border-border-terminal p-2.5 bg-primary/20">
                    <div className="flex justify-between items-center text-xs font-bold text-[#FFF] border-b border-border-terminal/40 pb-1 mb-1.5">
                      <span>BTC Order Target Hit</span>
                      <span className="text-success">+$827.40</span>
                    </div>
                    <p className="text-[#8F949E]">
                      <strong>Lesson:</strong> Spot ETF volume represents highly sticky capital. Volume profiles are highly predictive in strong macro regimes. Enforce stops.
                    </p>
                  </div>
                  
                  <div className="border border-border-terminal p-2.5 bg-primary/20">
                    <div className="flex justify-between items-center text-xs font-bold text-[#FFF] border-b border-border-terminal/40 pb-1 mb-1.5">
                      <span>ETH Order Blocked</span>
                      <span className="text-[#8F949E]">Vetoed</span>
                    </div>
                    <p className="text-[#8F949E]">
                      <strong>Lesson:</strong> Smart contract exploits present extreme systemic volatility. Risk gatekeeper VETO prevented buying a falling knife. Protection works.
                    </p>
                  </div>
                </div>
              )}

              {/* TAB 3: DEMO INJECTORS (Stage 15 Hackathon Demo) */}
              {activeRightTab === "demo" && (
                <div className="flex flex-col gap-3 font-mono text-[10px]">
                  <span className="text-[#8F949E] leading-4">
                    Trigger simulated market catalysts to run automated agent analyses, multi-round debate loops, consensus voting, risk manager checks, and execution order syntheses.
                  </span>
                  
                  <button 
                    disabled={isSimulating}
                    onClick={() => triggerSimulation("rally")}
                    className="w-full py-2.5 text-center font-bold tracking-wider text-[#FFF] bg-success border border-success hover:bg-success/90 transition-colors uppercase cursor-pointer disabled:opacity-40"
                  >
                    Simulate Bitcoin ETF Approval (Rally)
                  </button>

                  <button 
                    disabled={isSimulating}
                    onClick={() => triggerSimulation("crash")}
                    className="w-full py-2.5 text-center font-bold tracking-wider text-[#FFF] bg-danger border border-danger hover:bg-danger/90 transition-colors uppercase cursor-pointer disabled:opacity-40"
                  >
                    Simulate Smart Contract Exploit (Crash Veto)
                  </button>
                </div>
              )}

            </div>
          </div>
        </section>

      </main>
    </div>
  );
}
