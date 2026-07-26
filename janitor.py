import os
import time
import urllib.request
import urllib.error
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. STREAMLIT APP KEEP-ALIVE PING
# ==========================================
def ping_streamlit_app():
    """Sends a GET request to keep the Streamlit app active."""
    app_url = os.getenv("STREAMLIT_APP_URL")
    if not app_url:
        print("⚠️ STREAMLIT_APP_URL environment variable is not set. Skipping ping.")
        return

    print(f"📡 Pinging Streamlit app at {app_url}...")
    try:
        req = urllib.request.Request(
            app_url, 
            headers={"User-Agent": "JanitorPingBot/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print(f"✅ Ping successful! App is active.")
            else:
                print(f"⚠️ Ping received status code: {response.status}")
    except urllib.error.URLError as e:
        print(f"❌ Ping failed: {e.reason}")
    except Exception as e:
        print(f"❌ Unexpected error during ping: {e}")

# Run keep-alive ping
ping_streamlit_app()


# ==========================================
# 2. PINECONE VECTOR DB JANITOR SWEEP
# ==========================================
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

print(f"\n🧹 Running Janitor Sweep at {time.ctime()}...")
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