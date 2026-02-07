import networkx as nx
from typing import List, Dict, Optional, Set

class ReasoningEngine:
    """
    The core algorithm for Causal Chain Discovery in a Graph Forest.
    It connects news events to contract risks through Bridge Nodes.
    """

    def __init__(self):
        pass

    def find_bridge_nodes(self, G_base: nx.DiGraph, G_news: nx.DiGraph) -> Set[str]:
        """
        Identifies entities that exist in both the contract and the news.
        Logic: V_bridge = V_base ∩ V_news
        """
        nodes_base = set(G_base.nodes())
        nodes_news = set(G_news.nodes())
        bridge_nodes = nodes_base.intersection(nodes_news)
        return bridge_nodes

    def discover_causal_chain(self, G_base: nx.DiGraph, G_news: nx.DiGraph, start_event: str):
        """
        Finds the path from a news event to a contract obligation/risk.
        Algorithm: Multi-graph Pathfinding (BFS-based)
        """
        # 1. Identify where news meets contract
        bridges = self.find_bridge_nodes(G_base, G_news)
        
        if not bridges:
            return "No semantic connection found between the news and the contract."

        # 2. Compose a temporary Forest Graph for reasoning
        # We combine them to allow pathfinding across both domains
        composite_G = nx.compose(G_base, G_news)
        
        # 3. Search for paths from the start_event to any node in the base graph
        # specifically looking for nodes of type 'Risk' or 'Obligation'
        discovery_results = []
        
        # Identify target nodes in the base graph (e.g., legal clauses or risks)
        targets = [n for n, d in G_base.nodes(data=True) if d.get('type') in ['Risk', 'Obligation', 'Clause']]

        for target in targets:
            try:
                # Calculate the shortest path in the combined graph
                path = nx.shortest_path(composite_G, source=start_event, target=target)
                
                # Verify if the path actually crosses a bridge node 
                # (to ensure it's a valid cross-domain inference)
                if any(node in bridges for node in path):
                    discovery_results.append({
                        "target": target,
                        "path": path,
                        "length": len(path)
                    })
            except nx.NetworkXNoPath:
                continue

        # Sort results by path length (shortest path = highest causal link)
        discovery_results.sort(key=lambda x: x['length'])
        return discovery_results

    def get_formatted_chain(self, path: List[str], G_composite: nx.DiGraph) -> str:
        """
        Converts a path of nodes into a readable causal string.
        """
        readable_path = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge_data = G_composite.get_edge_data(u, v)
            rel_type = edge_data.get('type', 'relates to')
            readable_path.append(f"({u}) --[{rel_type}]--> ({v})")
        
        return " -> ".join(readable_path)

# --- Example of how this will be used in the main app ---
if __name__ == "__main__":
    # This is a conceptual test logic
    engine = ReasoningEngine()
    print("Reasoning Engine initialized.")
