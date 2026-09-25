import sqlite3
import pandas as pd
from logging_config import logger

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
            f"Write ONE valid SQL query (no explanation) to answer: {query}\n"
            f"Only reference tables and columns that exist in the schema above. "
            f"Do not join tables that use incompatible time granularities "
            f"(e.g. a monthly table and a quarterly table) unless there is a "
            f"shared column that maps between them. "
            f"SQLite strftime does not support a quarter format specifier — "
            f"never use '%q'. Prefer simpler queries over ones with unnecessary joins."
        )
        raw = self.llm_fn(prompt).strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            raw = raw.removeprefix("sql").strip()

        return raw.strip()

    def answer(self, query: str) -> str:
        sql = self._nl_to_sql(query)
        logger.info(f"Generated SQL: {sql}")

        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql, conn)
            conn.close()
        except Exception as e:
            logger.error(f"SQL execution failed for query {query!r}: {e} | SQL: {sql}")
            return f"SQL failed: {e}\nQuery: {sql}"

        if df.empty:
            logger.info(f"Query returned no results: {sql}")
            return f"No results found.\n\n[Generated SQL: {sql}]"

        return f"{df.to_string(index=False)}\n\n[Generated SQL: {sql}]"