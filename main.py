import sys
import os
import networkx as nx

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.reasoning_engine import ReasoningEngine

def find_news_root_cause(news_graph: nx.DiGraph):
    """
    Helper to find a starting point in the news graph.
    Heuristic: Pick a node with in-degree 0 (root cause).
    """
    for node in news_graph.nodes():
        if news_graph.in_degree(node) == 0:
            return node
    # Fallback: pick the first node
    return list(news_graph.nodes())[0] if news_graph.number_of_nodes() > 0 else None

def main():
    print("=== SGSA: GraphRAG Causal Discovery System ===\n")

    # 1. Load Data
    data_path = os.path.join("data/raw", "contracts_and_news.json")
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    loader = DataLoader(data_path)
    contracts = loader.load()
    
    # 2. Initialize Engine
    engine = ReasoningEngine()

    print(f"\nProcessing {len(contracts)} contracts for risk analysis...\n")

    # 3. Analyze each contract
    for contract in contracts:
        print(f"--- Contract: {contract.contract_id} ({contract.title}) ---")
        
        # Step A: Identify Bridge Nodes
        bridges = engine.find_bridge_nodes(contract.base_graph, contract.news_graph)
        if not bridges:
            print("  [!] No intersection between News and Contract. Skipping.")
            continue
        print(f"  [*] Bridge Nodes found: {bridges}")

        # Step B: Determine Start Event (Root of the news)
        start_event = find_news_root_cause(contract.news_graph)
        print(f"  [*] News Event Trigger: {start_event}")

        # Step C: Discover Causal Chain
        results = engine.discover_causal_chain(
            contract.base_graph, 
            contract.news_graph, 
            start_event
        )

        if results:
            print(f"  [+] {len(results)} potential risk paths discovered.")
            for i, res in enumerate(results): # Show all paths
                chain_str = engine.get_formatted_chain(
                    res['path'], 
                    nx.compose(contract.base_graph, contract.news_graph)
                )
                print(f"      Path {i+1}: {chain_str}")
        else:
            print("  [-] No causal path found to any Risk/Obligation.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
