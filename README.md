# Dynamic GraphRAG for Contract Risk Analysis

**Group 9 | Algorithm Design Project**

This repository implements a **Semantic Graph Analysis System** designed to detect supply chain risks by dynamically linking static contract data with real-time news events. It features two distinct implementation approaches: a pure algorithmic Graph Traversal engine and a Generative AI (GraphRAG) engine.

## 📌 Project Overview

In global supply chains, contracts rely on specific locations, logistics providers, and suppliers. When external events (e.g., Typhoons, Strikes, Sanctions) occur, they ripple through this network.
This project uses **Graph Theory** to:
1.  Model Contracts and News as Knowledge Graphs.
2.  Find "Bridge Nodes" connecting the two graphs.
3.  Trace the causal chain from an Event to a Contract Risk.

## 🚀 Key Features

### 1. Algorithmic Reasoning Engine (Branch: `main`)
*   **Technology:** Python, NetworkX.
*   **Logic:** Uses specific graph traversal algorithms (Bidirectional Search / BFS) to find paths between distinct graphs.
*   **Output:** Precise topological paths (e.g., `Event -> Location -> Supplier -> Product`).

### 2. GraphRAG Engine (Branch: `feature/neo4j-llm`)
*   **Technology:** Neo4j, LangChain, Google Gemini (LLM).
*   **Logic:** Ingests data into a Graph Database. Uses LLMs to translate natural language queries into **Cypher** queries to retrieve sub-graphs and generate human-readable risk summaries.
*   **Output:** Natural language explanation of the impact.

## 📂 Repository Structure

The repository is organized to support both approaches:

```text
Algorithm_Project_SemanticGraph_Group9/
├── data/
│   └── raw/
│       └── contracts_and_news.json      # The dataset containing Knowledge Graphs
├── src/
│   ├── data_loader.py                   # JSON Parsing & NetworkX Graph Construction
│   ├── reasoning_engine.py              # (Main) Algorithmic Path Finding
│   ├── graph_rag_engine.py              # (Feature) LLM & LangChain Logic
│   ├── neo4j_manager.py                 # (Feature) Database Connection & Ingestion
│   └── show_graphs.py                   # Visualization Tool (PyVis)
├── outputs/
│   ├── graphs/                          # HTML interactive visualizations
│   ├── main_output.txt                  # Logs from Algorithmic Engine
│   └── main_neo4j_output.txt            # Logs from GraphRAG Engine
├── docs/
│   └── report/                          # Project Report PDF
├── main.py                              # Entry point for Algorithmic Approach
├── main_neo4j.py                        # Entry point for GraphRAG Approach
└── requirements.txt                     # Dependencies
```

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.9+
*   **Neo4j Desktop** or AuraDB (for the GraphRAG branch)
*   Google Cloud API Key (for Gemini LLM)

### 1. Clone the Repository
```bash
git clone https://github.com/alikashipazha/Algorithm_Project_SemanticGraph_Group9.git
cd Algorithm_Project_SemanticGraph_Group9
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration (For GraphRAG)
Create a `.env` file in the root directory:
```ini
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
GOOGLE_API_KEY=your_google_gemini_key
```

## 🏃 Usage

### Option A: Run Algorithmic Analysis (NetworkX)
This runs the pure graph traversal logic found in `reasoning_engine.py`.
```bash
python main.py
```
*   **What happens:** It loads the JSON, identifies bridge nodes, performs BFS, and prints risk paths to the console.

### Option B: Run GraphRAG Analysis (Neo4j + LLM)
Ensure your Neo4j database is running.
```bash
python main_neo4j.py
```
*   **What happens:** It clears the DB, ingests the JSON data, and queries the LLM to analyze specific events (e.g., "Analyze Typhoon Krathon").

### Option C: Visualize Graphs
Generate HTML interactive graphs to see the connections.
```bash
python src/show_graphs.py
```
Check `outputs/graphs/*.html` to interact with the visualizations.

## 📊 Dataset Format
The `contracts_and_news.json` contains an array of objects:
```json
{
    "contract_id": "C01",
    "base_graph": { "entities": [...], "relations": [...] },
    "news_sequence": { "entities": [...], "relations": [...] }
}
```
*   **Base Graph:** Nodes = Companies, Ports, Products.
*   **News Sequence:** Nodes = Weather Events, Strikes, blocked Routes.

## 📝 Example Output

**Input Event:** `Typhoon_Krathon`

**Algorithmic Output:**
```text
Path 1: Typhoon_Krathon --(FLOODS)--> Kaohsiung_Region --(CLOSES)--> Port_of_Kaohsiung <--(SHIPPED_FROM)-- GPU_Chips
```

**GraphRAG Output:**
```text
Typhoon Krathon is approaching Taiwan and causing floods... This closure impacts the supply chain as GPU Chips are shipped from this port.
```