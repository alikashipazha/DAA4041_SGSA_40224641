import json
import os
import networkx as nx
from pyvis.network import Network

def generate_visualizations():
    # 1. Setup Paths
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # project_root = os.path.dirname(current_dir)
    json_path = r"data/raw/contracts_and_news.json"

    # 2. Direct JSON Loading (No DataLoader)
    # if not os.path.exists(json_path):
    #     print(f"[!] Error: File not found at {json_path}")
    #     return

    with open(json_path, 'r', encoding='utf-8') as f:
        contracts = json.load(f)

    print(f"[*] Successfully loaded {len(contracts)} contracts from JSON.")

    # 3. Iterate & Build
    for i, contract in enumerate(contracts):
        # Create a NetworkX graph to handle merging easily
        G = nx.DiGraph()
        
        # Track news nodes for coloring
        news_node_ids = set()

        # --- Process Base Graph ---
        base = contract.get("base_graph", {})
        for node in base.get("entities", []):
            G.add_node(node["id"], type=node["type"])
        
        for edge in base.get("relations", []):
            G.add_edge(edge["source"], edge["target"], label=edge["type"])

        # --- Process News Graph ---
        news = contract.get("news_sequence", {})
        for node in news.get("entities", []):
            nid = node["id"]
            G.add_node(nid, type=node["type"]) # Update/Add node
            news_node_ids.add(nid) # Mark as news
        
        for edge in news.get("relations", []):
            G.add_edge(edge["source"], edge["target"], label=edge["type"])

        # 4. Pyvis Visualization (EXACT User Settings)
        net = Network(
            height="800px",
            width="100%",
            directed=True,
            bgcolor="#ffffff",
            font_color="black"
        )

        net.barnes_hut(
            gravity=-25000,
            central_gravity=0.25,
            spring_length=300,   # Long edges
            spring_strength=0.02,
            damping=0.09
        )

        # 5. Add Nodes to Pyvis
        for node, attr in G.nodes(data=True):
            node_type = attr.get("type", "Unknown")
            
            # Color Logic: Red for News, Blue for Base
            if node in news_node_ids:
                color = "#ff4500" # Red
            else:
                color = "#00bfff" # Blue

            net.add_node(
                node,
                label=node,
                title=node_type,
                color=color,
                shape="ellipse",
                font={"size": 16}
            )

        # 6. Add Edges to Pyvis
        for u, v, attr in G.edges(data=True):
            net.add_edge(
                u,
                v,
                label=attr.get("label", ""),
                arrows="to",
                font={"size": 14}
            )

        # 7. Save
        output_path = os.path.join("outputs/graphs", f"c{i}.html")
        net.save_graph(output_path)
        print(f"    [+] Generated: {output_path}")

if __name__ == "__main__":
    generate_visualizations()
