import os
import networkx as nx
from pyvis.network import Network
from data_loader import DataLoader

def generate_visualizations():
    # 1. Load Data
    json_path = os.path.join("data", "contracts_and_news.json")
    loader = DataLoader(json_path)
    contracts = loader.load() #load_data()
    
    print(f"[*] Generating HTML visualizations for {len(contracts)} contracts...")

    # 2. Iterate and Generate
    for i, contract in enumerate(contracts):
        # Combine Base + News
        G_base = contract['base_graph']
        G_news = contract['news_graph']
        G_combined = nx.compose(G_base, G_news)
        
        # 3. Setup Pyvis Network (User Settings)
        net = Network(
            height="800px",
            width="100%",
            directed=True,
            bgcolor="#ffffff",
            font_color="black"
        )

        # Physics Settings (User Settings)
        net.barnes_hut(
            gravity=-25000,
            central_gravity=0.25,
            spring_length=300,
            spring_strength=0.02,
            damping=0.09
        )

        # 4. Add Nodes with Coloring
        # Logic: If node is in News Graph -> Red, Otherwise (Contract only) -> Blue
        news_nodes = set(G_news.nodes())
        
        for node, attr in G_combined.nodes(data=True):
            node_type = attr.get("type", "Entity")
            
            # Determine Color
            if node in news_nodes:
                color = "#ff4500"  # Red (OrangeRed) for News/Bridge
            else:
                color = "#00bfff"  # Blue (DeepSkyBlue) for Contract Base
            
            net.add_node(
                node,
                label=node,
                title=node_type, # Tooltip shows Type
                color=color,
                shape="ellipse",
                font={"size": 16}
            )

        # 5. Add Edges
        for u, v, data in G_combined.edges(data=True):
            relation = data.get("type", "RELATED")
            net.add_edge(
                u,
                v,
                label=relation,
                arrows="to",
                font={"size": 14}
            )

        # 6. Save File
        filename = f"c{i}.html"
        net.save_graph(filename)
        print(f"    [+] Saved: {filename}")

if __name__ == "__main__":
    generate_visualizations()
