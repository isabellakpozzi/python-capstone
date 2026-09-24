import sqlite3, pandas as pd

class QuantitativeAgent:
    def __init__(self, db_path, llm_fn):
        self.db_path = db_path
        self.llm_fn = llm_fn
        conn = sqlite3.connect(db_path)
        self.schema = "\n".join(r[0] for r in conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table'") if r[0])
        conn.close()

    def answer(self, query: str) -> str:
        prompt = f"Schema:\n{self.schema}\n\nWrite ONE SQL query (no explanation) for: {query}"
        sql = self.llm_fn(prompt).strip().strip("```sql").strip("```")
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql, conn)
            conn.close()
        except Exception as e:
            return f"SQL failed: {e}\nQuery: {sql}"
        return df.to_string(index=False) if not df.empty else "No results found."