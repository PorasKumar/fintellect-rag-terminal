import uuid
from pinecone import Pinecone
from pinecone import ServerlessSpec
import os
from dotenv import load_dotenv
load_dotenv()

class UpsertData:
    def __init__(self, chunks, dense_embeddings, sparse_embeddings, namespace):
        self.chunks = chunks
        self.dense_embeddings = dense_embeddings
        self.sparse_embeddings = sparse_embeddings
        self.namespace = namespace

        #initialise the pinecone index, create if does not exist
        try:
            pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
            self.index_name = os.environ.get("PINECONE_INDEX_NAME")
            if not pc.has_index(self.index_name):
                pc.create_index(
                    name=self.index_name,
                    dimension=384,
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                    metric="dotproduct"
                    )
            self.index = pc.Index(self.index_name) #pinecone index
        except Exception as e:
            print(f"\n\nError in initialising pinecone index:\n\n{e}")
            raise RuntimeError("Error in initialising Pinecone Index")
        

    def upsert_the_data_func(self):
        
        #prepare the payload
        pinecone_upsert_payload = []
        for i, (chunk, dense_emb, sparse_emb) in enumerate(zip(self.chunks, self.dense_embeddings, self.sparse_embeddings)):
            mtdata = chunk.metadata
            mtdata["page_content"] = chunk.page_content
            mtdata["doc_index"] = i
            mtdata["content_length"] = len(chunk.page_content)

            record = {
                "id": f"doc_{uuid.uuid4().hex[0:8]}_{i}",
                "values":dense_emb,
                "sparse_values":sparse_emb,
                "metadata":mtdata
            }

            pinecone_upsert_payload.append(record)
            

        #upserting the data

        #upserting in batches of 100
            
        batch_size = 100
        print(f"Upserting data in batches of {batch_size}")
        for i in range(0, len(pinecone_upsert_payload), batch_size):
            batch = pinecone_upsert_payload[i:i+batch_size]
            self.index.upsert(
                vectors=batch,
                namespace=self.namespace
            )
            print(f"Upserted batches: {i} to {i+len(batch)}")
        
        
        
    
    def delete_namespace(self):
        try:
            stats = self.index.describe_index_stats()
            existing_namespaces = stats.get('namespaces', {})

            if (self.namespace in existing_namespaces):
                print(f"\nExisting namespace found called : {self.namespace}")
                print(f'Deleting namespace: {self.namespace}')
                self.index.delete(delete_all=True, namespace=self.namespace)
            else:
                print(f"Namespace: {self.namespace} does not exist")
        
        except Exception as e:
            print(f"Error in deleting namespace! {e}")
            raise RuntimeError("Error in deleting the namespace!")