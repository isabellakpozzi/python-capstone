import sqlite3
import pandas as pd


class QuantitativeAgent:
    def __init__(self, db_path: str, llm_fn):
        self.db_path = db_path
        self.llm_fn = llm_fn
        self.schema = self._get_schema()

    def _get_schema(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        schema = "\n".join(row[0] for row in cursor.fetchall() if row[0])
        conn.close()
        return schema

    def _nl_to_sql(self, query: str) -> str:
        prompt = (
            f"Given this SQLite schema:\n{self.schema}\n\n"
            f"Write ONE valid SQL query (no explanation) to answer: {query}"
        )
        raw = self.llm_fn(prompt).strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            raw = raw.removeprefix("sql").strip()

        return raw.strip()

    def answer(self, query: str) -> str:
        sql = self._nl_to_sql(query)
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql, conn)
            conn.close()
        except Exception as e:
            return f"SQL failed: {e}\nQuery: {sql}"

        if df.empty:
            return "No results found."
        return f"{df.to_string(index=False)}\n\n[Generated SQL: {sql}]"