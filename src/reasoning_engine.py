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

    def discover_causal_chain(self, base_graph: nx.DiGraph, news_graph: nx.DiGraph, start_event: str):
        """
        Finds paths from the start_event (News) to any Risk/Penalty (Contract).
        Uses bidirectional traversal (successors + predecessors) on the Directed Graph
        to trace risk propagation upstream without altering graph structure.
        """
        # 1. Combine graphs (Directed)
        G_combined = nx.compose(base_graph, news_graph)
        
        # 2. Define potential target types
        target_types = {
            "Risk", "RiskCondition", "FinancialCondition", "Obligation", 
            "Penalty", "Condition", "Prohibition", "Product"
        }
        
        targets = set()
        for node, attr in G_combined.nodes(data=True):
            if attr.get("type") in target_types:
                targets.add(node)
        
        # Fallback: Contract Owner
        if not targets:
            for node, attr in G_combined.nodes(data=True):
                if attr.get("type") == "Company":
                    targets.add(node)

        results = []
        
        if not G_combined.has_node(start_event):
            return []

        # 3. Custom BFS for Risk Propagation (Upstream + Downstream)
        # We search for ALL targets and store the shortest path to them.
        queue = [[start_event]]
        visited = {start_event}
        
        found_paths = []

        while queue:
            path = queue.pop(0)
            node = path[-1]

            # If we hit a target node (that is not the start node itself)
            if node in targets and node != start_event:
                found_paths.append(path)
                # Optimization: To find multiple potential risks, we don't break immediately,
                # but for simplicity in this snippet, we can collect valid paths.
                continue
            
            # Stop if path gets too long (heuristic to prevent infinite loops in complex cycles)
            if len(path) > 10:
                continue

            # CRITICAL FIX: Look at both outgoing (successors) and incoming (predecessors)
            # This allows tracing "Factory -> LOCATED_IN -> Country" backwards from Country to Factory.
            neighbors = list(G_combined.successors(node)) + list(G_combined.predecessors(node))
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        # Format results
        for p in found_paths:
            target_node = p[-1]
            results.append({
                "target": target_node,
                "path": p,
                "length": len(p)
            })

        # Sort by shortest path first
        results.sort(key=lambda x: x['length'])
        return results

    def get_formatted_chain(self, path, combined_graph):
        """
        Formats the path list into a readable string.
        Since we traversed bidirectionally, we check edge direction to show correct flow.
        """
        chain_str = f"{path[0]}"
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            
            # Check if forward edge exists (u -> v)
            if combined_graph.has_edge(u, v):
                edge_data = combined_graph.get_edge_data(u, v)
                rel_type = edge_data.get('type', 'RELATED')
                relation = f"--({rel_type})-->"
            
            # Check if backward edge exists (v -> u)
            elif combined_graph.has_edge(v, u):
                edge_data = combined_graph.get_edge_data(v, u)
                rel_type = edge_data.get('type', 'RELATED')
                # Arrow points back, meaning we traversed upstream
                relation = f"<--({rel_type})--"
            
            else:
                relation = "--(?)-"
            
            chain_str += f" {relation} {v}"
        
        return chain_str

# --- Example of how this will be used in the main app ---
if __name__ == "__main__":
    # This is a conceptual test logic
    engine = ReasoningEngine()
    print("Reasoning Engine initialized.")
