# 📈 Financial Data Search Agent (Hybrid RAG)

A real-time financial search engine built with **LangChain**, **Pinecone**, and **Streamlit**. 
The system combines dense semantic vector retrieval with sparse keyword matching 
(**Hybrid Search**) and real-time web search 
(**Tavily API**) to answer complex financial queries with high precision and fresh data.

## 🏗 Architecture Overview

•	-->Input: Take the user query as input.
•	-->Web Search: Search the web for relevant context using the Tavily Search API.
•	-->Document Structuring: Convert and store raw search results into standard LangChain.Document format.
•	-->Text Chunking: Split the retrieved documents using RecursiveCharacterTextSplitter to optimize chunk sizes for embedding.
•	-->Hybrid Embedding: Calculate dense embeddings via HuggingFace models and sparse embeddings via BM25 for the document text.
•	-->Vector Storage: Upsert the generated dense and sparse vectors into the Pinecone vector database.
•	-->Targeted Retrieval: Query Pinecone to retrieve only the most relevant context chunks using the original user query.
•	-->Synthesis: Pass the retrieved context along with the user query to Gemini to generate a grounded, summarized response.



## ✨ Key Features

* **Hybrid Search Retrieval:** Blends dense vector representations (HuggingFace) with BM25 sparse keyword matching in Pinecone to balance deep semantic understanding with exact entity/financial terminology matching.
* **Fallback Web Retrieval:** Integrates Tavily API for live web search when domain queries require real-time market updates or out-of-index financial reports.
* **Automated Memory Hygiene (Janitor Function):** Features an automated background cleanup routine that scans Pinecone namespaces and purges dormant sessions older than 3 hours, keeping vector storage lean and budget-conscious.
* **Document Chunking & Ingestion:** Ingests complex financial documents, applying optimized text-splitting strategies to preserve context windows.
* **Streamlit UI:** Simple, reactive dashboard for running queries, inspecting retrieved source contexts, and viewing LLM output.


Checkout the app: https://fintellect-rag-terminal.streamlit.app/
