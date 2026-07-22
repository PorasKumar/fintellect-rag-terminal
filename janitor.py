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

# Fetch all namespaces
try:
    stats = index.describe_index_stats()
    namespaces = stats.get("namespaces", {})
except Exception as e:
    print(f"❌ Failed to fetch index stats from Pinecone: {e}")
    exit(1)

current_time = time.time()
MAX_AGE_SECONDS = 10800  # 3 hours (10800 seconds)

print(f"🧹 Running Janitor Sweep at {time.ctime()}...")
print(f"Found {len(namespaces)} active namespaces.")

for nmspc in list(namespaces.keys()):
    try:
        # Expecting format USERNAME_ID_TIMESTAMP
        parts = nmspc.split("_")
        timestamp_str = parts[-1]
        nmspc_timestamp = float(timestamp_str)

        # Check if namespace age is more than MAX_AGE_SECONDS
        if (current_time - nmspc_timestamp) > MAX_AGE_SECONDS:
            print(f"🗑️ Deleting expired namespace: {nmspc}")
            
            # Compatible with all Pinecone SDK versions
            try:
                index.delete(delete_all=True, namespace=nmspc)
            except AttributeError:
                # Fallback for newer SDK versions
                index.delete_all(namespace=nmspc)

        else:
            print(f"⏳ Keeping active namespace: {nmspc}")

    except (ValueError, IndexError):
        # Skip namespaces that don't match our timestamp format (e.g., default namespace)
        print(f"⚠️ Skipping non-standard namespace: {nmspc}")
    except Exception as e:
        print(f"❌ Failed to delete namespace '{nmspc}': {e}")

print("✨ Janitor sweep completed successfully!")