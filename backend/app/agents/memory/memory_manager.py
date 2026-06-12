"""
Agent Memory Manager
Handles semantic memory storage and retrieval for Council AI agents.

Supports:
- OpenAI embedding generation (1536 dimensions)
- Supabase pgvector storage & RPC matching queries
- Local JSON file fallback with NumPy-based cosine similarity
- Hybrid ranking strategy combining similarity, recency decay, and importance
"""

import os
import json
import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class AgentMemoryManager:
    """
    Manages persistent memory and semantic search for AI agents.
    
    Tries to connect to Supabase, but falls back to local JSON storage
    with local numpy-based vector similarity calculation if Supabase is unavailable.
    """
    
    def __init__(self, local_storage_path: Optional[str] = None):
        """
        Initialize the Memory Manager.
        
        Args:
            local_storage_path: Custom path for local JSON fallback. Defaults to agent_memory.json.
        """
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        # Determine local path
        if not local_storage_path:
            # Place it in the App Data brain folder or current dir
            self.local_path = "agent_memory.json"
        else:
            self.local_path = local_storage_path
            
        self.supabase_client = None
        self.use_supabase = False
        
        # Try to initialize Supabase client if credentials are present
        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.supabase_client = create_client(self.supabase_url, self.supabase_key)
                self.use_supabase = True
                logger.info("AgentMemoryManager initialized with Supabase client.")
            except ImportError:
                logger.warning("supabase-py not installed. Falling back to local file memory.")
            except Exception as e:
                logger.warning(f"Failed to connect to Supabase: {e}. Falling back to local file memory.")
        else:
            logger.info("Supabase credentials not found. Using local JSON fallback for agent memory.")
            
        # Initialize Embeddings model
        self.embeddings_model = None
        if self.openai_api_key and self.openai_api_key != "mock-key":
            try:
                try:
                    from langchain_openai import OpenAIEmbeddings
                    self.embeddings_model = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
                except ImportError:
                    try:
                        from langchain_community.embeddings import OpenAIEmbeddings
                        self.embeddings_model = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
                    except ImportError:
                        from langchain.embeddings import OpenAIEmbeddings
                        self.embeddings_model = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
                logger.info("OpenAIEmbeddings model loaded successfully.")
            except Exception as e:
                logger.warning(f"Failed to load OpenAIEmbeddings: {e}. Using deterministic mock embeddings.")

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generate a 1536-dimensional embedding vector for the text.
        
        Uses OpenAI if available, otherwise falls back to a deterministic hash-based mock.
        """
        if self.embeddings_model:
            try:
                return self.embeddings_model.embed_query(text)
            except Exception as e:
                logger.warning(f"OpenAI embedding generation failed: {e}. Using mock fallback.")
                
        # Deterministic hash-based mock embedding for offline/testing robustness
        # Generates a pseudo-random vector of length 1536 seeded by text hash
        import hashlib
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        
        # Generate random vector and normalize it to unit length (so dot product equals cosine similarity)
        vector = rng.normal(0.0, 1.0, 1536)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.tolist()

    def add_memory(
        self,
        agent_id: str,
        content: str,
        memory_type: str,
        symbol: Optional[str] = None,
        market_conditions: Optional[str] = None,
        relevance_score: float = 0.50,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a new memory record for an agent.
        
        Args:
            agent_id: ID of the agent
            content: The text description of what happened or what was learned
            memory_type: 'past_trade', 'past_analysis', 'lesson_learned'
            symbol: Asset symbol, e.g. BTC
            market_conditions: 'bullish', 'bearish', 'volatile', 'stable'
            relevance_score: Importance level (0.0 to 1.0)
            tags: List of descriptive string tags
            
        Returns:
            The created memory record dictionary
        """
        tags = tags or []
        embedding = self._get_embedding(content)
        created_at = datetime.utcnow().isoformat() + "Z"
        
        memory_record = {
            "agent_id": agent_id,
            "memory_type": memory_type,
            "content": content,
            "symbol": symbol,
            "market_conditions": market_conditions,
            "relevance_score": float(relevance_score),
            "tags": tags,
            "embedding": embedding,
            "created_at": created_at,
            "last_retrieved_at": created_at,
            "retrieval_count": 0
        }
        
        if self.use_supabase:
            try:
                res = self.supabase_client.table("agent_memory").insert(memory_record).execute()
                logger.info(f"Memory successfully stored in Supabase for agent {agent_id}.")
                return res.data[0] if res.data else memory_record
            except Exception as e:
                logger.error(f"Failed to insert memory to Supabase: {e}. Saving locally.")
                
        # Local JSON file fallback
        self._add_memory_locally(memory_record)
        return memory_record

    def retrieve_memories(
        self,
        agent_id: str,
        query: str,
        limit: int = 5,
        symbol: Optional[str] = None,
        market_conditions: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for an agent using a hybrid ranking strategy.
        
        Args:
            agent_id: ID of the agent
            query: The search query (e.g. current market state text)
            limit: Maximum memories to return
            symbol: Optional symbol filter
            market_conditions: Optional market conditions filter
            
        Returns:
            List of ranked memory records with matching scores
        """
        query_embedding = self._get_embedding(query)
        
        raw_memories = []
        
        if self.use_supabase:
            try:
                # Call pgvector match rpc function on Supabase
                # match_memories(query_embedding, match_threshold, match_count, filter_agent_id, filter_symbol, filter_market_conditions)
                params = {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.0,  # Retrieve all relevant to run hybrid ranking locally
                    "match_count": limit * 3,
                    "filter_agent_id": agent_id,
                    "filter_symbol": symbol,
                    "filter_market_conditions": market_conditions
                }
                res = self.supabase_client.rpc("match_memories", params).execute()
                if res.data:
                    raw_memories = res.data
                    logger.info(f"Retrieved {len(raw_memories)} memories from Supabase.")
            except Exception as e:
                logger.error(f"Supabase memory search failed: {e}. Falling back to local search.")
                self.use_supabase = False  # Temporarily disable
                raw_memories = self._retrieve_memories_locally(agent_id, symbol, market_conditions)
                self.use_supabase = True
        else:
            raw_memories = self._retrieve_memories_locally(agent_id, symbol, market_conditions)
            
        # If no memories found, return empty list
        if not raw_memories:
            return []
            
        # Calculate cosine similarity if it wasn't pre-calculated by Supabase RPC
        # (local retrieval doesn't have similarity calculated yet)
        query_vec = np.array(query_embedding)
        for mem in raw_memories:
            if "similarity" not in mem and "embedding" in mem:
                mem_vec = np.array(mem["embedding"])
                dot_product = np.dot(query_vec, mem_vec)
                norm_q = np.linalg.norm(query_vec)
                norm_m = np.linalg.norm(mem_vec)
                similarity = dot_product / (norm_q * norm_m) if norm_q > 0 and norm_m > 0 else 0.0
                mem["similarity"] = similarity
            elif "similarity" not in mem:
                mem["similarity"] = 0.5  # Fallback
                
        # 3. Apply hybrid ranking: Similarity (50%), Recency (30%), Importance/Relevance (20%)
        ranked_memories = self._rank_memories(raw_memories)
        
        # Slice to limit
        final_memories = ranked_memories[:limit]
        
        # Async-style update retrieval statistics in background
        self._update_retrieval_stats(final_memories)
        
        return final_memories

    def _rank_memories(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank memories using a hybrid scoring algorithm.
        
        Score = 0.50 * similarity + 0.30 * recency_decay + 0.20 * relevance_score
        Recency Decay = exp(-0.05 * age_in_days)
        """
        ranked = []
        now = datetime.utcnow()
        
        for mem in memories:
            similarity = float(mem.get("similarity", 0.0))
            relevance = float(mem.get("relevance_score", 0.5))
            
            # Parse created_at
            created_str = mem.get("created_at", "")
            try:
                # Handle iso timestamps
                if created_str.endswith("Z"):
                    created_str = created_str[:-1]
                created_dt = datetime.fromisoformat(created_str)
                age_days = max(0.0, (now - created_dt).total_seconds() / 86400.0)
            except Exception:
                age_days = 0.0
                
            # Recency exponential decay (half-life of ~14 days, lambda = 0.05)
            recency_decay = math.exp(-0.05 * age_days)
            
            # Combined score
            hybrid_score = (
                0.50 * similarity +
                0.30 * recency_decay +
                0.20 * relevance
            )
            
            # Store score
            mem_copy = mem.copy()
            # Clean up embedding from output to keep data footprint small
            if "embedding" in mem_copy:
                del mem_copy["embedding"]
            mem_copy["hybrid_score"] = round(hybrid_score, 4)
            mem_copy["age_days"] = round(age_days, 2)
            mem_copy["recency_decay"] = round(recency_decay, 4)
            
            ranked.append(mem_copy)
            
        # Sort by hybrid score descending
        ranked.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return ranked

    def _update_retrieval_stats(self, memories: List[Dict[str, Any]]):
        """Update retrieval statistics for the selected memories."""
        now_str = datetime.utcnow().isoformat() + "Z"
        
        # If Supabase, we can update async in background or run updates
        if self.use_supabase:
            for mem in memories:
                try:
                    mem_id = mem.get("id")
                    if mem_id:
                        # Fetch current and increment
                        self.supabase_client.table("agent_memory").update({
                            "last_retrieved_at": now_str,
                            "retrieval_count": int(mem.get("retrieval_count", 0)) + 1
                        }).eq("id", mem_id).execute()
                except Exception as e:
                    logger.warning(f"Failed to update Supabase retrieval stats: {e}")
                    
        # Always update local JSON as well if using it
        try:
            if os.path.exists(self.local_path):
                with open(self.local_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                updated = False
                for mem in memories:
                    mem_id = mem.get("id")
                    # Local memory might match by content if UUID isn't stored
                    for local_mem in data:
                        if (mem_id and local_mem.get("id") == mem_id) or (local_mem.get("content") == mem.get("content") and local_mem.get("agent_id") == mem.get("agent_id")):
                            local_mem["last_retrieved_at"] = now_str
                            local_mem["retrieval_count"] = local_mem.get("retrieval_count", 0) + 1
                            updated = True
                            
                if updated:
                    with open(self.local_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to update local retrieval stats: {e}")

    # Local storage helpers
    def _add_memory_locally(self, record: Dict[str, Any]):
        """Save a memory record to the local JSON file."""
        import uuid
        record = record.copy()
        record["id"] = str(uuid.uuid4())
        
        memories = []
        try:
            if os.path.exists(self.local_path):
                with open(self.local_path, "r", encoding="utf-8") as f:
                    memories = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read local memory file: {e}. Creating new file.")
            
        memories.append(record)
        
        try:
            with open(self.local_path, "w", encoding="utf-8") as f:
                json.dump(memories, f, indent=2)
            logger.info(f"Memory successfully stored locally in {self.local_path}.")
        except Exception as e:
            logger.error(f"Failed to write memory locally: {e}")

    def _retrieve_memories_locally(
        self,
        agent_id: str,
        symbol: Optional[str] = None,
        market_conditions: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filter local memory records by agent_id and optional filters."""
        if not os.path.exists(self.local_path):
            return []
            
        try:
            with open(self.local_path, "r", encoding="utf-8") as f:
                memories = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read local memory file: {e}")
            return []
            
        filtered = []
        for mem in memories:
            if mem.get("agent_id") != agent_id:
                continue
            if symbol and mem.get("symbol") != symbol:
                continue
            if market_conditions and mem.get("market_conditions") != market_conditions:
                continue
            filtered.append(mem)
            
        return filtered
