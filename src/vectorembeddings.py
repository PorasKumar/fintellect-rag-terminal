from sentence_transformers import SentenceTransformer
from pinecone_text.sparse import BM25Encoder
from dotenv import load_dotenv
load_dotenv()
import os

class VectorEmbeddings:
    def __init__(self, texts_in_chunks):
        self.texts_in_chunks = texts_in_chunks

        #load dense model
        try:
            HF_TOKEN = os.environ.get("HF_TOKEN")
            self.dense_model_name = "all-MiniLM-L6-v2"
            self.dense_model = SentenceTransformer(self.dense_model_name)
            print(f"Embedding Dimension HuggingFace: {self.dense_model.get_embedding_dimension()}")
        except Exception as e:
            print(f"Error loading HuggingFace Model {e}\n\n")
            raise RuntimeError("Error Loading HugginFace Model for Sentence Transforming")

        #load bm25
        try:
            self.bm25 = BM25Encoder()
        except Exception as e:
            print(f"\n\nError loading BM25 Encoder {e}")
            raise RuntimeError("Error loading BM25 Encoder!\n\n")


    def dense_embedding_documents(self):
        try:
            dense_embeddings = self.dense_model.encode(self.texts_in_chunks).tolist()
            return dense_embeddings
        
        except Exception as e:
            print(f"\n\nError in Dense Embedding generation\n\n{e}")
            raise RuntimeError("Error in generating embeddings for Chunks using Dense Model HuggingFace")
    
    def sparse_embedding_documents(self):
        try:
            self.bm25.fit(self.texts_in_chunks)

            sparse_embeddings = self.bm25.encode_documents(self.texts_in_chunks)
            return sparse_embeddings
        
        except Exception as e:
            print(f"\n\nError in Sparse Embedding generation\n\n{e}")
            raise RuntimeError("Error in generating embeddings for Chunks using Sparse Model BM25")