import sys
import os
from src.data_loader import DataLoader
from src.neo4j_manager import Neo4jManager
from src.graph_rag_engine import GraphRAGEngine

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("=== GraphRAG with Neo4j & LLM ===\n")

    # 1. Load Data from JSON
    data_path = os.path.join("data/raw", "contracts_and_news.json")
    loader = DataLoader(data_path)
    contracts = loader.load()

    # 2. Initialize Neo4j Manager
    neo_manager = Neo4jManager()
    
    # Optional: Clear DB to start fresh
    neo_manager.clear_database()

    # 3. Ingest Data into Neo4j
    print("\n--- Ingesting Data into Graph Database ---")
    for contract in contracts:
        neo_manager.ingest_contract_data(contract)
    
    # 4. Initialize GraphRAG Engine
    rag_engine = GraphRAGEngine()

    print("\n--- Starting LLM-based Risk Analysis ---")
    
    # Let's analyze a specific case (e.g., Typhoon Krathon from Contract C01)
    # In a real app, you would loop through all or ask user input.
    
    test_cases = [
        ("Typhoon_Krathon", "C01"),
        ("Trade_Union_GDL", "C03")
    ]

    for event, contract_id in test_cases:
        print(f"\n[?] Analyzing Impact of: {event} (Contract {contract_id})")
        
        # The Magic Happens Here:
        # The LLM generates the Cypher query, runs it against Neo4j, 
        # reads the result, and synthesizes an answer.
        analysis = rag_engine.analyze_risk(event)
        
        print(f"\n[LLM Response]:\n{analysis}")
        print("-" * 50)

    # Cleanup
    neo_manager.close()

if __name__ == "__main__":
    main()