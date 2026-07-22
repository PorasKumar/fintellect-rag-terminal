from typing import Any
class RelevantDocSearch:
    def __init__(self, index, namespace, scaled_dense_query: list, scaled_sparse_query:dict[str,Any]):
        self.index = index
        self.namespace = namespace
        self.scaled_dense_query = scaled_dense_query
        self.scaled_sparse_query = scaled_sparse_query
    
    def search_relevant_docs_from_pinecone(self):
            results = self.index.query(
                namespace = self.namespace,
                vector =self.scaled_dense_query,
                sparse_vector = self.scaled_sparse_query,
                include_metadata = True,
                top_k = 12,
            )

            return results
        