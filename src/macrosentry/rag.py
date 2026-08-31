"""Phase 2: RAG - Vector store and context retrieval from historical FOMC statements."""
import logging
from typing import Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

class VectorStore:
    """Simple in-memory vector store with embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with sentence-transformers (runs locally, no API needed)."""
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = np.array([])
        self.metadata = []

    def add_documents(self, texts: list[str], metadata: list[dict] = None):
        """Add documents to the store."""
        if not texts:
            return

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        self.documents.extend(texts)
        self.embeddings = np.vstack([self.embeddings, embeddings]) if len(self.embeddings) > 0 else embeddings
        self.metadata.extend(metadata or [{"source": "unknown"} for _ in texts])
        logger.info(f"Added {len(texts)} documents to vector store")

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve top-k similar documents."""
        if len(self.embeddings) == 0:
            logger.warning("Vector store is empty")
            return []

        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]

        # Cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        top_indices = np.argsort(-similarities)[:top_k]

        results = [
            {
                "text": self.documents[i],
                "score": float(similarities[i]),
                "metadata": self.metadata[i]
            }
            for i in top_indices
        ]

        return results

    def save(self, path: str):
        """Save vector store to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({
                "documents": self.documents,
                "embeddings": self.embeddings,
                "metadata": self.metadata,
            }, f)
        logger.info(f"Saved vector store to {path}")

    def load(self, path: str):
        """Load vector store from disk."""
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.documents = data["documents"]
        self.embeddings = data["embeddings"]
        self.metadata = data["metadata"]
        logger.info(f"Loaded vector store from {path}")


class RAGPipeline:
    """RAG retrieval for classification context."""

    def __init__(self):
        self.vector_store = VectorStore()
        self._seed_historical_fomc()

    def _seed_historical_fomc(self):
        """Seed the vector store with historical FOMC statements."""
        # Simplified historical FOMC text samples (in production: parse actual FOMC minutes)
        historical_statements = [
            "The Committee decided to raise the target range for the federal funds rate to 5.25 to 5.50 percent. The inflation rate over the past year has declined notably but remains somewhat elevated.",
            "In light of the significant progress on inflation in recent months, the Committee judged that the risks to achieving its employment and inflation goals are now roughly balanced.",
            "The Committee will continue to assess the appropriate stance of monetary policy based on incoming data, the economic outlook, and financial conditions.",
            "Inflation has moderated from recent highs, though it remains above the Committee's longer-run goal of 2 percent.",
            "The Committee expects that some additional increases in the target range for the federal funds rate may be appropriate to return inflation to 2 percent over time.",
            "Economic activity has picked up recently after having slowed in the first quarter. The labor market remains solid.",
            "The Committee decided to leave the target range for the federal funds rate unchanged at 5.00 to 5.25 percent.",
            "Inflation has declined notably from recent highs, and conditions have improved overall.",
            "Against this backdrop, the Committee judged that the risks are moving toward better balance.",
            "The Committee will continue to monitor incoming data and carefully assess the appropriate path for monetary policy.",
        ]

        metadata = [
            {"source": "fomc_statement", "date": "2024-01-31"},
            {"source": "fomc_statement", "date": "2024-03-20"},
            {"source": "fomc_statement", "date": "2024-05-01"},
            {"source": "fomc_statement", "date": "2024-06-18"},
            {"source": "fomc_statement", "date": "2024-07-31"},
            {"source": "fomc_statement", "date": "2024-09-18"},
            {"source": "fomc_statement", "date": "2024-11-06"},
            {"source": "fomc_statement", "date": "2024-12-18"},
            {"source": "fomc_statement", "date": "2025-01-29"},
            {"source": "fomc_statement", "date": "2025-03-19"},
        ]

        self.vector_store.add_documents(historical_statements, metadata)

    def retrieve_context(self, query: str, top_k: int = 3) -> list[str]:
        """Retrieve historical FOMC context for a query."""
        results = self.vector_store.retrieve(query, top_k=top_k)
        return [r["text"] for r in results]

    def format_context_for_classification(self, query: str) -> str:
        """Format retrieved context for LLM classification."""
        context_docs = self.retrieve_context(query, top_k=2)
        context_str = "\n".join([f"- {doc}" for doc in context_docs])
        return f"Historical FOMC context:\n{context_str}"


# CLI for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    rag = RAGPipeline()

    test_queries = [
        "Fed raises interest rates to combat inflation",
        "Powell says policy is appropriately restrictive",
        "Inflation moderates from recent highs",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        context = rag.retrieve_context(query)
        for i, doc in enumerate(context, 1):
            print(f"  {i}. {doc[:80]}...")
