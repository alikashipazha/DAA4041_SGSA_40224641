import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Neo4jManager:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        """Wipes the database clean before loading new data."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("[Neo4j] Database cleared.")

    def ingest_contract_data(self, contract_data):
        """
        Takes a single ContractData object (from your existing DataLoader)
        and inserts nodes/relationships into Neo4j using Cypher.
        """
        with self.driver.session() as session:
            # 1. Insert Base Graph
            self._insert_graph(session, contract_data.base_graph, "Base")
            
            # 2. Insert News Graph
            self._insert_graph(session, contract_data.news_graph, "News")
            
            print(f"[Neo4j] Ingested contract: {contract_data.contract_id}")

    def _insert_graph(self, session, nx_graph, graph_category):
        """
        Helper to iterate NetworkX nodes/edges and run Cypher MERGE.
        """
        # Insert Nodes
        for node_id, attrs in nx_graph.nodes(data=True):
            node_type = attrs.get("type", "Entity")
            # We use MERGE to avoid duplicates.
            # Label includes the specific type (e.g., :Company) and a generic :Entity
            query = f"""
            MERGE (n:Entity {{id: $id}})
            SET n:{node_type}, n.category = $category
            """
            session.run(query, id=node_id, category=graph_category)

        # Insert Edges
        for u, v, attrs in nx_graph.edges(data=True):
            rel_type = attrs.get("type", "RELATED_TO")
            # Cypher requires relationship types to be static strings usually, 
            # but we can handle dynamic types with APOC or specific query formatting.
            # For safety here, we construct the query string (ensure rel_type is safe/sanitized).
            query = f"""
            MATCH (a:Entity {{id: $source}}), (b:Entity {{id: $target}})
            MERGE (a)-[r:`{rel_type}`]->(b)
            SET r.category = $category
            """
            session.run(query, source=u, target=v, category=graph_category)