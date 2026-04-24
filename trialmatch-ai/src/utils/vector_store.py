"""
TrialMatch AI — Vector Store (Qdrant)
Embeds trial eligibility criteria and performs semantic search.
Supports: in-memory mode (no server needed) or Qdrant server.
"""
import json
import hashlib
from typing import List, Dict, Optional
from pathlib import Path


class TrialVectorStore:
    """
    Qdrant-based vector store for trial eligibility criteria.
    
    Modes:
    - In-memory: No Qdrant server needed. Data lives in RAM. Good for demo/testing.
    - Server: Connects to Qdrant at a URL. Persistent storage.
    
    Usage:
        store = TrialVectorStore()              # in-memory
        store = TrialVectorStore(url="http://localhost:6333")  # server
        
        store.index_trials(trials)              # embed and store
        results = store.search("EGFR NSCLC", top_k=5)  # semantic search
    """
    
    COLLECTION_NAME = "trial_eligibility"
    
    def __init__(self, url: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        self.url = url
        self.embedding_model_name = embedding_model
        self._model = None
        self._client = None
        self._collection_ready = False
    
    def _get_model(self):
        """Lazy-load the sentence transformer model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.embedding_model_name)
        return self._model
    
    def _get_client(self):
        """Lazy-load the Qdrant client."""
        if self._client is None:
            from qdrant_client import QdrantClient
            if self.url:
                self._client = QdrantClient(url=self.url)
            else:
                # In-memory mode — no server needed
                self._client = QdrantClient(":memory:")
        return self._client
    
    def _ensure_collection(self, vector_size: int):
        """Create collection if it doesn't exist."""
        if self._collection_ready:
            return
        from qdrant_client.models import Distance, VectorParams
        client = self._get_client()
        
        collections = [c.name for c in client.get_collections().collections]
        if self.COLLECTION_NAME not in collections:
            client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
        self._collection_ready = True
    
    def _chunk_criteria(self, eligibility_text: str) -> List[str]:
        """
        Split eligibility criteria into individual criterion chunks.
        Strategy: split on newlines and bullet points (per-criterion chunking).
        """
        if not eligibility_text:
            return []
        
        chunks = []
        lines = eligibility_text.replace("\r\n", "\n").split("\n")
        current_section = ""  # "inclusion" or "exclusion"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            lower = line.lower()
            if "inclusion" in lower and "criteria" in lower:
                current_section = "inclusion"
                continue
            elif "exclusion" in lower and "criteria" in lower:
                current_section = "exclusion"
                continue
            
            # Remove bullet points and numbering
            clean = line.lstrip("•·-*0123456789.) ")
            if len(clean) > 10:  # skip very short lines
                prefix = f"[{current_section.upper()}] " if current_section else ""
                chunks.append(f"{prefix}{clean}")
        
        # If no chunks found (no newline-separated criteria), split on periods
        if not chunks and len(eligibility_text) > 50:
            sentences = eligibility_text.split(". ")
            chunks = [s.strip() + "." for s in sentences if len(s.strip()) > 10]
        
        return chunks if chunks else [eligibility_text]
    
    def index_trials(self, trials: List[Dict]) -> int:
        """
        Embed and index trial eligibility criteria into Qdrant.
        
        Args:
            trials: List of trial dicts with at least 'nct_id' and 'eligibility_criteria'
        
        Returns:
            Number of chunks indexed
        """
        model = self._get_model()
        client = self._get_client()
        
        # Collect all chunks with metadata
        all_chunks = []
        for trial in trials:
            nct_id = trial.get("nct_id", "")
            criteria_text = trial.get("eligibility_criteria", "")
            title = trial.get("title", "")
            phase = trial.get("phase", "")
            
            chunks = self._chunk_criteria(criteria_text)
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.md5(f"{nct_id}_{i}_{chunk[:50]}".encode()).hexdigest()
                all_chunks.append({
                    "id": chunk_id,
                    "text": chunk,
                    "nct_id": nct_id,
                    "title": title,
                    "phase": phase,
                    "chunk_index": i,
                })
        
        if not all_chunks:
            return 0
        
        # Embed all chunks
        texts = [c["text"] for c in all_chunks]
        embeddings = model.encode(texts, show_progress_bar=False)
        vector_size = embeddings.shape[1]
        
        # Ensure collection exists
        self._ensure_collection(vector_size)
        
        # Upload to Qdrant
        from qdrant_client.models import PointStruct
        
        points = []
        for i, (chunk, embedding) in enumerate(zip(all_chunks, embeddings)):
            points.append(PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={
                    "text": chunk["text"],
                    "nct_id": chunk["nct_id"],
                    "title": chunk["title"],
                    "phase": chunk["phase"],
                    "chunk_index": chunk["chunk_index"],
                },
            ))
        
        client.upsert(collection_name=self.COLLECTION_NAME, points=points)
        return len(points)
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Semantic search for trials matching a query.
        
        Args:
            query: Natural language query (e.g., "EGFR positive NSCLC Phase 3")
            top_k: Number of results to return
        
        Returns:
            List of dicts with nct_id, title, text, score
        """
        model = self._get_model()
        client = self._get_client()
        
        query_vector = model.encode(query).tolist()
        
        try:
            results = client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_vector,
                limit=top_k,
            )
            
            # Deduplicate by nct_id (multiple chunks from same trial)
            seen = {}
            output = []
            for hit in results:
                nct = hit.payload.get("nct_id", "")
                if nct not in seen:
                    seen[nct] = True
                    output.append({
                        "nct_id": nct,
                        "title": hit.payload.get("title", ""),
                        "phase": hit.payload.get("phase", ""),
                        "matched_criterion": hit.payload.get("text", ""),
                        "score": round(hit.score, 4),
                    })
            return output
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_stats(self) -> Dict:
        """Get collection statistics."""
        try:
            client = self._get_client()
            info = client.get_collection(self.COLLECTION_NAME)
            return {
                "collection": self.COLLECTION_NAME,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status.value,
                "embedding_model": self.embedding_model_name,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def delete_collection(self):
        """Delete the collection."""
        try:
            client = self._get_client()
            client.delete_collection(self.COLLECTION_NAME)
            self._collection_ready = False
            return True
        except:
            return False
