import os
import time
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()

# 1. Initialize Pinecone client
api_key = os.environ.get("PINECONE_API_KEY")
index_name = os.environ.get("PINECONE_INDEX_NAME")

if not api_key or not index_name:
    print("❌ Missing Pinecone environment variables.")
    exit(1)

pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

#fetch all namespaces
stats = index.describe_index_stats()
namespaces = stats.get("namespaces",{})

current_time = time.time()
MAX_AGE_SECONDS = 300 #max time for a namespace to live

print(f"🧹 Running Janitor Sweep at {time.ctime()}...")
print(f"Found {len(namespaces)} active namespaces.")

for nmspc in list(namespaces.keys()):
    try:
        #expecting format USERNAME_ID_TIMESTAMP
        parts = nmspc.split("_")
        timestamp_str = parts[-1] #timestamp is at the end of username
        nmspc_timestamp = float(timestamp_str)

        #check if namespace age is more than MAX_AGE_SECONDS
        if (current_time - nmspc_timestamp) > MAX_AGE_SECONDS:
            print(f"🗑️ Deleting expired namespace: {nmspc}")
            index.delete(delete_all=True, namespace=nmspc)
        else:
            print(f"Keeping active namespace: {nmspc}")

    except (ValueError, IndexError):
    # Skip namespaces that don't match our timestamp format (e.g., default namespace)
        print(f"⚠️ Skipping non-standard namespace: {nmspc}")


print("✨ Janitor sweep completed successfully!")