import unittest
import os
import json
import tempfile
import sys
import networkx as nx

# Add src to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loader import DataLoader

class TestDataLoader(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary JSON file for testing."""
        self.test_data = [
            {
                "contract_id": "C_TEST_01",
                "title": "Test Contract",
                "contract_text": "Sample text.",
                "base_graph": {
                    "entities": [{"id": "A", "type": "T1"}, {"id": "B", "type": "T2"}],
                    "relations": [{"source": "A", "target": "B", "type": "R1"}]
                },
                "news_sequence": {
                    "entities": [{"id": "X", "type": "E1"}],
                    "relations": []
                }
            }
        ]
        
        # Create a temp file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
        json.dump(self.test_data, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        """Remove the temp file after test."""
        os.remove(self.temp_file.name)

    def test_load_contract_count(self):
        """Ensure it loads the correct number of contracts."""
        loader = DataLoader(self.temp_file.name)
        contracts = loader.load()
        self.assertEqual(len(contracts), 1)
        self.assertEqual(contracts[0].contract_id, "C_TEST_01")

    def test_graph_construction(self):
        """Ensure JSON is converted to NetworkX graphs correctly."""
        loader = DataLoader(self.temp_file.name)
        contracts = loader.load()
        contract = contracts[0]

        # Check Base Graph
        self.assertIsInstance(contract.base_graph, nx.DiGraph)
        self.assertTrue(contract.base_graph.has_node("A"))
        self.assertTrue(contract.base_graph.has_edge("A", "B"))
        
        # Check News Graph
        self.assertIsInstance(contract.news_graph, nx.DiGraph)
        self.assertTrue(contract.news_graph.has_node("X"))

if __name__ == '__main__':
    unittest.main()
