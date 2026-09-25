import chromadb
from chromadb.utils import embedding_functions
from logging_config import logger


class QualitativeAgent:
    def __init__(self, docs_path: str, llm_fn, chroma_path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="enterprise_docs", embedding_function=self.embedder
        )
        self.llm_fn = llm_fn
        self._index_if_empty(docs_path)

    def _index_if_empty(self, docs_path):
        import os
        if self.collection.count() > 0:
            return
        for fname in os.listdir(docs_path):
            with open(os.path.join(docs_path, fname)) as f:
                text = f.read()
            self.collection.add(documents=[text], ids=[fname], metadatas=[{"source": fname}])

    def answer(self, query: str, top_k: int = 3, max_distance: float = 0.9) -> str:
        results = self.collection.query(query_texts=[query], n_results=top_k)
        docs = results["documents"][0]
        distances = results["distances"][0]
        sources = results["metadatas"][0]
        ids = results["ids"][0]

        if not distances or distances[0] > max_distance:
            logger.info(f"No relevant sources found for query: {query!r}")
            return "I couldn't find relevant documentation for that question."

        kept = list(zip(docs, sources, distances, ids))
        source_names = [src["source"] for _, src, _, _ in kept]
        logger.info(f"Retrieved sources: {source_names}")

        context = "\n\n".join(doc for doc, _, _, _ in kept)
        prompt = f"Answer using ONLY this context:\n{context}\n\nQuestion: {query}"

        try:
            answer_text = self.llm_fn(prompt)
        except Exception as e:
            logger.error(f"LLM call failed for query {query!r}: {e}")
            return f"Failed to generate an answer: {e}"

        citation_lines = "\n".join(
            f"  - {src['source']} (id: {doc_id}, similarity score: {1 - dist:.3f})"
            for _, src, dist, doc_id in kept
        )
        return f"{answer_text}\n\nSources:\n{citation_lines}"