import os
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain # آپدیت شده برای رفع Warning
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class GraphRAGEngine:
    def __init__(self):
        # 1. اتصال به Neo4j با استفاده از کلاس جدید
        self.graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("کلید GOOGLE_API_KEY در فایل .env یافت نشد!")

        # 2. راه‌اندازی مدل جمنای
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            temperature=0,
            google_api_key=google_api_key
        )

        self.graph.refresh_schema()

    def analyze_risk(self, news_event_id: str):
        # این پرامپت به مدل یاد می‌دهد که کوئری استاندارد و سبک بنویسد
        # cypher_generation_template = """
        # Task: Generate a Cypher statement to query a graph database.
        # Instructions:
        # 1. Find paths starting from a node where id = '{event_id}'.
        # 2. Limit the path depth to maximum 3 steps: -[*1..3]-
        # 3. Use undirected relationships (--) to find any connection.
        # 4. If you need to filter by multiple labels, use this syntax:
        #    WHERE labels(m) IN ['Risk', 'Penalty', 'Company', 'Product'] 
        #    or just match the connections without complex filters.
        # 5. Return the path 'p'.
        
        # Schema:
        # {schema}
        
        # Question: {question}
        
        # Cypher Query:"""
        cypher_generation_template = """
        Task: Generate a Cypher statement to query a graph database.
        Instructions:
        1. Find paths starting from a node where id = '{event_id}'.
        2. Limit the path depth to maximum 3 steps: -[*1..3]-
        3. Use undirected relationships (--) to find all connected entities.
        4. IMPORTANT: Do not filter by specific labels like 'Company' or 'Supplier' unless requested. 
           Just return the whole path 'p' to see all connections.
        5. Do not include any markdown formatting.
        
        Schema:
        {schema}
        
        Question: {question}
        
        Cypher Query:"""

        
        cypher_prompt = PromptTemplate(
            template=cypher_generation_template,
            input_variables=["schema", "question", "event_id"]
        )

        # ساخت زنجیره با تنظیمات اصلاحی
        chain = GraphCypherQAChain.from_llm(
            self.llm,
            graph=self.graph,
            verbose=True,
            cypher_prompt=cypher_prompt,
            validate_cypher=True, # این گزینه خطاهای سینتکسی را اصلاح می‌کند
            allow_dangerous_requests=True
        )

        query = f"Analyze the impact of the event '{news_event_id}' on contracts and companies. List the chain of affected entities."

        try:
            # ارسال متغیرها به پرامپت
            result = chain.invoke({
                "query": query, 
                "event_id": news_event_id
            })
            return result['result']
        except Exception as e:
            return f"Error in GraphRAG analysis: {str(e)}"