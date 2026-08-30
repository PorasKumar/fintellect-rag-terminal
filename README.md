# 📈 Financial Data Search Agent (Hybrid RAG)

A real-time financial search engine built with **LangChain**, **Pinecone**, and **Streamlit**. 
The system combines dense semantic vector retrieval with sparse keyword matching 
(**Hybrid Search**) and real-time web search 
(**Tavily API**) to answer complex financial queries with high precision and fresh data.

## 🏗 Architecture Overview
1.) Take the user query as input
2.) Search the web using Tavily Search API
3.) Store the results in LangChain.Document format
4.) Splitting and Chunking using Recursive Character Text Splitter
5.) Then calculate Dense and Sparse embeddings for the raw text of the Searched Documents (HuggingFace(dense) & BM25(sparse))
6.) Upserting the data to Pinecone vector Database
7.) Retrieve only the relevant chunks using the same query
8.) Send the retrieved context and user query to LLM (gemini-3.1-flash used) to generate a meaningful and summarised result.


## ✨ Key Features

* **Hybrid Search Retrieval:** Blends dense vector representations (HuggingFace) with BM25 sparse keyword matching in Pinecone to balance deep semantic understanding with exact entity/financial terminology matching.
* **Fallback Web Retrieval:** Integrates Tavily API for live web search when domain queries require real-time market updates or out-of-index financial reports.
* **Automated Memory Hygiene (Janitor Function):** Features an automated background cleanup routine that scans Pinecone namespaces and purges dormant sessions older than 3 hours, keeping vector storage lean and budget-conscious.
* **Document Chunking & Ingestion:** Ingests complex financial documents, applying optimized text-splitting strategies to preserve context windows.
* **Streamlit UI:** Simple, reactive dashboard for running queries, inspecting retrieved source contexts, and viewing LLM output.


Checkout the app: https://fintellect-rag-terminal.streamlit.app/
