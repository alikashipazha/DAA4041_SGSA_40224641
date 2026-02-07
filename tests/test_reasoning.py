import unittest
import networkx as nx
import sys
import os

# Adjust path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reasoning_engine import ReasoningEngine

class TestReasoningEngine(unittest.TestCase):
    
    def setUp(self):
        """Setup dummy graphs before each test."""
        self.engine = ReasoningEngine()
        
        # 1. Base Graph (The Contract)
        # Structure: Supplier -> Material -> Product (Risk)
        self.G_base = nx.DiGraph()
        self.G_base.add_node("Supplier_A", type="Entity")
        self.G_base.add_node("Material_X", type="Resource")
        self.G_base.add_node("Product_Risk", type="Risk") # Target
        self.G_base.add_edge("Supplier_A", "Material_X", type="provides")
        self.G_base.add_edge("Material_X", "Product_Risk", type="affects")

        # 2. News Graph (The Event)
        # Structure: Storm -> Region -> Supplier_A
        self.G_news = nx.DiGraph()
        self.G_news.add_node("Storm_Z", type="Event") # Start
        self.G_news.add_node("Region_Y", type="Location")
        self.G_news.add_node("Supplier_A", type="Entity") # Bridge Node
        self.G_news.add_edge("Storm_Z", "Region_Y", type="hits")
        self.G_news.add_edge("Region_Y", "Supplier_A", type="disrupts")

    def test_find_bridge_nodes(self):
        """Test if the engine identifies the common node correctly."""
        bridges = self.engine.find_bridge_nodes(self.G_base, self.G_news)
        self.assertIn("Supplier_A", bridges)
        self.assertEqual(len(bridges), 1)

    def test_causal_chain_discovery(self):
        """Test if it finds the path from Storm_Z to Product_Risk."""
        # Expected Path: Storm_Z -> Region_Y -> Supplier_A -> Material_X -> Product_Risk
        results = self.engine.discover_causal_chain(self.G_base, self.G_news, start_event="Storm_Z")
        
        self.assertTrue(len(results) > 0, "Should find at least one path")
        
        best_result = results[0]
        path = best_result['path']
        
        self.assertEqual(path[0], "Storm_Z")
        self.assertEqual(path[-1], "Product_Risk")
        self.assertIn("Supplier_A", path, "Path must cross the bridge node")

if __name__ == '__main__':
    unittest.main()
