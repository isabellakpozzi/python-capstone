import chromadb
from chromadb.utils import embedding_functions

class QualitativeAgent:
    def __init__(self, docs_path, llm_fn):
        self.client = chromadb.PersistentClient(path="./chroma_db")
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

    def answer(self, query: str, top_k=3) -> str:
        results = self.collection.query(query_texts=[query], n_results=top_k)
        context = "\n\n".join(results["documents"][0])
        sources = ", ".join(m["source"] for m in results["metadatas"][0])
        prompt = f"Answer using ONLY this context:\n{context}\n\nQuestion: {query}"
        return f"{self.llm_fn(prompt)}\n\n[Sources: {sources}]"