from llm import mock_llm
from agents.manager import ManagerAgent
from agents.qualitative_agent import QualitativeAgent
from agents.quantitative_agent import QuantitativeAgent
from system import build_system

def main():
    # manager = build_system(llm_fn=call_llm)  
    manager = build_system(llm_fn=mock_llm)
    print("=== Enterprise Docs Assistant ===")
    print("Ask a qualitative or quantitative question, or 'exit' to quit.\n")

    while True:
        query = input("> ").strip()
        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            print("Goodbye.")
            break
        result = manager.handle_query(query)
        print(f"\n[{result['type'].upper()}]\n{result['response']}\n")

if __name__ == "__main__":
    main()