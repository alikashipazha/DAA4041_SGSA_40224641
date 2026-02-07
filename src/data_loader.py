import json
import networkx as nx
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ContractData:
    """
    Data structure holding the parsed contract and its associated news graph.
    """
    contract_id: str
    title: str
    contract_text: str
    base_graph: nx.DiGraph
    news_graph: nx.DiGraph

class DataLoader:
    """
    Responsible for loading raw JSON data and converting it into 
    NetworkX graph objects for the reasoning engine.
    """

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)

    def _json_to_graph(self, graph_data: Dict) -> nx.DiGraph:
        """
        Converts a dictionary with 'entities' and 'relations' into a NetworkX DiGraph.
        """
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for entity in graph_data.get("entities", []):
            # entity = {"id": "...", "type": "..."}
            G.add_node(entity["id"], type=entity["type"])
            
        # Add edges with attributes
        for relation in graph_data.get("relations", []):
            # relation = {"source": "...", "target": "...", "type": "..."}
            G.add_edge(
                relation["source"], 
                relation["target"], 
                type=relation["type"]
            )
            
        return G

    def load(self) -> List[ContractData]:
        """
        Parses the JSON file and returns a list of ContractData objects.
        """
        if not self.filepath.exists():
            raise FileNotFoundError(f"Dataset not found at: {self.filepath}")

        with open(self.filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        contracts = []
        for entry in raw_data:
            # Parse Base Graph (Contract)
            base_G = self._json_to_graph(entry.get("base_graph", {}))
            
            # Parse News Graph (Sequence)
            news_G = self._json_to_graph(entry.get("news_sequence", {}))

            contract_obj = ContractData(
                contract_id=entry.get("contract_id"),
                title=entry.get("title"),
                contract_text=entry.get("contract_text"),
                base_graph=base_G,
                news_graph=news_G
            )
            contracts.append(contract_obj)

        print(f"Successfully loaded {len(contracts)} contracts from {self.filepath.name}")
        return contracts

# --- Quick Test Block (Optional, requires main execution) ---
if __name__ == "__main__":
    # Assuming the json file is in ../data/processed/ relative to src/
    import os
    
    # Path setup for testing inside src/ folder
    # base_dir = Path(__file__).resolve().parent.parent
    data_path = r"data\\contracts_and_news.json"
    
    # Create dummy file if not exists for testing logic only (Commented out for real usage)
    # In real usage, ensure contracts_and_news.json exists at the path
    
    try:
        loader = DataLoader(str(data_path))
        data = loader.load()
        
        # Verify first item
        if data:
            c1 = data[0]
            print(f"\n--- Inspection: {c1.contract_id} ---")
            print(f"Base Graph Nodes: {c1.base_graph.number_of_nodes()}")
            print(f"Base Graph Edges: {c1.base_graph.number_of_edges()}")
            print(f"News Graph Nodes: {c1.news_graph.number_of_nodes()}")
            
            # Check a node attribute
            node_sample = list(c1.base_graph.nodes(data=True))[0]
            print(f"Sample Node: {node_sample}")
            
    except Exception as e:
        print(f"Error during test: {e}")
