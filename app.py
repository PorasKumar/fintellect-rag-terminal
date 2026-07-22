import streamlit as st
import uuid
import time
import logging
# Mute Streamlit's loud internal file-watcher tracking logs
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)


st.set_page_config(page_title="Financial RAG Terminal", layout="wide")

glass_css = """
<style>
    /* Prevent full screen scrolling entirely */
    html, body, .stApp {
        background: linear-gradient(135deg, #0a192f 0%, #122540 35%, #234b70 75%, #3b6d9c 100%);
        color: #f1f5f9;
        height: 100vh !important;
        overflow: hidden !important;
    }

    /* Hardware-accelerated sunrise animation */
    @keyframes sunrise {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Smooth upward slide & fade keyframe for UI transitions */
    @keyframes slideUpInput {
        0% {
            opacity: 0;
            transform: translateY(18px) scale(0.98);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .brand-title { 
        animation: sunrise 0.4s ease-out forwards; 
        color: #ffffff; 
        font-size: 2.8rem; 
        font-weight: 800;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .brand-tagline { 
        animation: sunrise 0.5s ease-out 0.08s forwards; 
        opacity: 0; 
        color: #38bdf8; 
        font-size: 1.2rem;
        font-weight: 400;
        margin-top: 5px;
        margin-bottom: 20px;
    }
    .brand-mic { 
        animation: sunrise 0.6s ease-out 0.15s forwards; 
        opacity: 0; 
        color: rgba(255, 255, 255, 0.6); 
        font-size: 1rem;
        font-weight: 300;
        letter-spacing: 1px;
    }

    /* Screen size responsive container to block scrolling entirely */
    .auth-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin: 18vh auto 2vh auto;
        max-width: 480px;
        padding: 30px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
    }

    /* Apply a distinct, clean glassy text box container around BOTH inputs */
    div[data-testid="stTextInput"] > div,
    .stChatInput > div {
        background: rgba(10, 25, 47, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        outline: none !important;
        transition: border-color 0.35s cubic-bezier(0.25, 1, 0.5, 1), 
                    box-shadow 0.35s cubic-bezier(0.25, 1, 0.5, 1),
                    background-color 0.35s cubic-bezier(0.25, 1, 0.5, 1) !important;
    }

    /* Smooth entrance animation for the chat input container on state refresh */
    .stChatInput {
        animation: slideUpInput 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
        will-change: transform, opacity;
    }

    /* Smooth placeholder text color transition */
    .stChatInput textarea::placeholder {
        transition: opacity 0.3s ease, color 0.3s ease !important;
    }

    /* Completely isolate and strip down the inner sub-elements to ensure zero red bleed */
    div[data-testid="stTextInput"] div, 
    div[data-testid="stTextInput"] input,
    div[data-baseweb="base-input"],
    div[data-baseweb="input"] {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* Elegant hover state for both fields */
    div[data-testid="stTextInput"] > div:hover,
    .stChatInput > div:hover {
        border-color: rgba(56, 189, 248, 0.6) !important;
        box-shadow: 0 0 35px rgba(56, 189, 248, 0.2) !important;
    }

    /* Massive, blurry premium sky-blue ambient focus glow when active/clicked */
    div[data-testid="stTextInput"] > div:focus-within,
    .stChatInput > div:focus-within {
        border-color: #38bdf8 !important;
        background: rgba(10, 25, 47, 0.8) !important;
        box-shadow: 0 0 45px rgba(56, 189, 248, 0.4) !important;
    }

    /* Keep text entries clean white globally */
    div[data-testid="stTextInput"] input, 
    .stChatInput textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* --- SLEEK PURE CSS ACTION BUTTON INTERACTIONS --- */
    .stButton > button {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transform: translateY(0) scale(1);
        transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1),
                    border-color 0.3s ease, 
                    box-shadow 0.3s ease,
                    background-color 0.2s ease !important;
    }
    
    /* Spring hover with subtle blue bloom aura */
    .stButton > button:hover {
        background: rgba(56, 189, 248, 0.12) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.25) !important;
        transform: translateY(-2px) scale(1.02);
    }

    /* Snappy responsive compression when clicked */
    .stButton > button:active {
        transform: translateY(1px) scale(0.97) !important;
        background: rgba(56, 189, 248, 0.25) !important;
        box-shadow: 0 2px 8px rgba(56, 189, 248, 0.15) !important;
        transition: transform 0.05s linear !important;
    }

    section[data-testid="stSidebar"] {
        background: #0a192f !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* --- MAIN INTERFACE ENTRANCE TRANSITIONS --- */
    .stMainBlockContainer {
        animation: sunrise 0.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }
    
    section[data-testid="stSidebar"] { 
        background: #0a192f !important; 
        border-right: 1px solid rgba(255, 255, 255, 0.08); 
        animation: sunrise 0.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }
    
    .chat-scroll-container {
        max-height: 70vh;
        overflow-y: auto;
        padding-right: 10px;
    }
    div[data-testid="stChatMessage"] {
        background: rgba(10, 25, 47, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
"""
st.markdown(glass_css, unsafe_allow_html=True)


#initialise session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'userid' not in st.session_state:
    st.session_state.userid = None

#backend logic session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'upsert_obj' not in st.session_state:
    st.session_state.upsert_obj = None
if 'upsert_count' not in st.session_state:
    st.session_state.upsert_count = 0
if 'talk_with_ai_count' not in st.session_state: #necessary to ignore tavilysearch, embedd, upsert everytime on rerun()
    st.session_state.talk_with_ai_count = 0
if 'chat_placeholder' not in st.session_state: #We change it to different placeholder when talking with AI
        st.session_state.chat_placeholder = ("Ask a financial question... e.g., 'Impacts of war global stock markets'")
if 'embeddings_obj' not in st.session_state: #need to use this everytime we rerun() for AI response after upserting
        st.session_state.embeddings_obj = None


#Teardown trigger flags (Logout and New Chat animation on bottom)
if 'pending_action' not in st.session_state:
    st.session_state.pending_action = None


# Helper function to wipe active vector resources
def cleanup_vector_resources():
    if (
        st.session_state.upsert_count == 1
        and st.session_state.upsert_obj is not None
    ):
        try:
            st.session_state.upsert_obj.delete_namespace()
        except Exception as e:
            print(f"Error purging vector namespace: {e}")
        st.session_state.upsert_count = 0
    st.session_state.upsert_obj = None



#authenticate user : LOGIN WINDOW : BEGIN FINTELLECT
if not st.session_state.authenticated:
    
    # Injecting custom raw HTML structure to enforce absolute alignment, name of the app and mic is yours is displayed by html,css
    st.markdown(
        '''
        <div class="auth-container">
            <div class="brand-title">Fintellect</div>
            <div class="brand-tagline">Your AI co-pilot for financial research.</div>
        </div>
        ''', 
        unsafe_allow_html=True
    )


    #main logic authentication window
    col1, col2, col3 = st.columns([1, 1.8, 1]) #to add everything in middle
    with col2:
        name_input = st.text_input("User Login Name:",placeholder="Enter your name to begin chat! e.g., Larry Page"
                                   ,label_visibility="collapsed")
        #to add button right in the middle of column 2, we have to make 3 more columns, looks clean
        #that is how we do it in streamlit bruh
        b_col1, b_col2, b_col3 = st.columns([1,1.2,1])
        with b_col2:
            lets_go_btn = st.button("Let's Go", use_container_width=True)

    if lets_go_btn:
        if not name_input:
            st.error("Please Enter your name to start searching")
        
        elif name_input:
            name_input = name_input.strip()
            #we will add current time stamp in name itself to delete dormant namespaces using janitor.py
            current_timestamp = int(time.time())
            #below creating a unique user id which will be used for namespaces too
            st.session_state.userid = f"{name_input.replace(" ","")}_{uuid.uuid4().hex[0:16]}_{current_timestamp}"
            st.session_state.username = name_input
            st.session_state.authenticated = True
            st.rerun() #will rerun it right after the authentication done


#if authenticated 
else:
    st.sidebar.title("Your Info")
    st.sidebar.write(f"Name: {st.session_state.username}")
    st.sidebar.write(f"User ID: {st.session_state.userid}")


    #new chat button
    if st.sidebar.button("✨ New Chat", use_container_width=True):
        st.session_state.pending_action = "new_chat"


    #delete the namespace here on LOGOUT
    if st.sidebar.button("Logout"):
        st.session_state.pending_action = "logout"
    


    #start the chat UI
    st.title(f"🎤The mic is yours, {st.session_state.username.split()[0]}") #split picks only first name
    st.caption("⚡ Powered by LangChain • Gemini • Pinecone • Tavily • HuggingFace")


    #loop to keep printing the chat in realtime on every st.rerun()
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    #USER QUERY INITIALISATION
    user_query = st.chat_input(st.session_state.chat_placeholder)

    #caption
    st.caption("⚠️ *Fintellect is an AI application and can make mistakes. Double-check critical financial data.*")

    #if user enters a query
    if user_query:

        try:
            st.session_state.messages.append({"role":"user", "content":user_query}) #list[dict] to differentiate b/w user and system
            with st.chat_message("user"):
                st.write(user_query)

            #here the pipeline will run
            with st.status("Executing pipeline operations.....", expanded=True) as status:
                
                log_slot = st.empty() #for displaying loading messages in st.status
                relevant_results = [] #when talking with AI, keep searching relevant docs to chat. Isko bahar isliye rakha hai kyuki upsert ke baad relevant search bar bar hogi har query pe

                if(st.session_state.talk_with_ai_count == 0):
                    
                    #retrieve from Tavily
                    from src.searchdocs import SearchDocs
                    log_slot.write("🔍 Initializing financial web search via Tavily...")
                    tavily_obj = SearchDocs(user_query)
                    raw_docs_from_tavily = tavily_obj.search_docs_tavily()

                    if not raw_docs_from_tavily:
                        raise RuntimeError("No document data could be found for your query")
                    
                    log_slot.empty()
                    log_slot.write(F"Found {len(raw_docs_from_tavily)} from tavily advanced search")

                    
                    #splitting and chunking docs
                    from src.splitting import SplitText
                    log_slot.empty()
                    log_slot.write("🧩 Splitting documents into chunks")
                    split_obj = SplitText(raw_docs_from_tavily)
                    chunks = split_obj.split_document_texts(800,150)
                    log_slot.empty()
                    log_slot.write(f"🧩 Split {len(raw_docs_from_tavily)} documents to {len(chunks)} chunks")


                    #embeddings generation
                    from src.vectorembeddings import VectorEmbeddings
                    log_slot.empty()
                    log_slot.write("🔗Initialising HuggingFace and BM25 for embeddings")
                    all_texts_in_chunks = [doc.page_content for doc in chunks]#extract texts from chunks
                    st.session_state.embeddings_obj = VectorEmbeddings(all_texts_in_chunks)
                    log_slot.empty()
                    log_slot.write("🔢Generating Dense Embeddings🧬")
                    dense_embeddings = st.session_state.embeddings_obj.dense_embedding_documents()
                    log_slot.empty()
                    log_slot.write("🔢Generating sparse embeddings🧬")
                    sparse_embeddings = st.session_state.embeddings_obj.sparse_embedding_documents()

                    #upserting the values (namespace logic, be very vigilant)
                    from src.upsertdata import UpsertData
                    log_slot.empty()
                    log_slot.write("🗄️⚙️⚛️🖥️ Initialising Pinecone to upsert data")
                    st.session_state.upsert_obj = UpsertData(chunks, dense_embeddings, sparse_embeddings,st.session_state.userid)
                    log_slot.empty()
                    log_slot.write("📥Upserting data to Pinecone....🚀")
                    
                    #using try except here to check if success in upsert so that we can make st.session_state.upsert_count = 1
                    try:
                        st.session_state.upsert_obj.upsert_the_data_func()
                        log_slot.write("Upserted Successfully")
                        st.session_state.upsert_count = 1
                    except Exception as e:
                        print(f"\n\nError in Upserting to Pinecone: \n\n{e}")
                        raise RuntimeError("Error in Upserting Data to Pinecone Server!")
                    


                # scaling query and retrieve relevant documents below

                # this code should only run when there is some data in Pinecone because what the hell will you retrieve if there is nothing
                
                #this code should run everytime so that when chatting with AI, it should keep retrieving relevant docs
                if (st.session_state.upsert_count == 1):
                    try:
                        from src.scale_query import ScaleQuery
                        log_slot.empty()
                        log_slot.write("🌿Scaling Query for Hybrid Search🔮")
                        scale_obj = ScaleQuery(user_query,
                                               st.session_state.embeddings_obj.dense_model,
                                               st.session_state.embeddings_obj.bm25,
                                               alpha=0.5)
                        scaled_dense_query, scaled_sparse_query = scale_obj.scale_query_func()
                        #relevant docs retrieve
                        from src.relevant_doc_search import RelevantDocSearch
                        relevant_search_obj = RelevantDocSearch(st.session_state.upsert_obj.index,
                                                                st.session_state.userid, 
                                                                scaled_dense_query,
                                                                scaled_sparse_query)
                        #we need results so that we can keep talking to gemini
                        relevant_results = relevant_search_obj.search_relevant_docs_from_pinecone()
                            
                        #talk_with_ai_count = 1 , because after retrieving user will ask questions from AI only
                        st.session_state.talk_with_ai_count = 1
                        st.session_state.chat_placeholder = "Chat with AI: Ask questions based on retrieved documents or You can start new chat"
                    
                    except Exception as e:
                        print(f"Error in finding relevant results in RelevantDocSearch\n\n\nException:{e}")
                        raise RuntimeError("Error in retrieving relevant documents, Start New Chat")


                if(st.session_state.talk_with_ai_count == 1):
                    #Generate AI Response from Google-Genai
                    from src.generate_ai_response import AIResponse
                    ai_obj = AIResponse(user_query, relevant_results)
                    answer = ai_obj.generate_ai_response_function()
   
                    #updating the status
                    status.update(label="✨ Analysis Completed!", state="complete", expanded=False)

            #print the ai answer and append it to st.session_state.messages 
            with st.spinner("📊 Crunching indices & synthesizing market intelligence..."):
                # 3. Print the AI answer in real-time streaming mode
                with st.chat_message("assistant"):
                    full_response = st.write_stream(answer)
            #append the st.session_state.messages (list[]) with ai answer and then rerun(). 
            #Since we need to keep track of messages in the session so that rerun() does not forget
            st.session_state.messages.append({"role": "assistant", "content": full_response})


            st.rerun() # no need, when code ends, streamlit handles rerun on its own


        except Exception as e:
            pipeline_exception = "Error executing query: "
            print(pipeline_exception,f"\n\n{e}")
            st.error(f"{pipeline_exception}\n\n {e}")
        
    
    # --- BOTTOM STATUS TEARDOWN ANIMATIONS ---
    # Renders teardown status containers at the absolute bottom of chats when actions are triggered
    #new chat aur login ka animation at bottom of chat and not at top

    if st.session_state.pending_action == "new_chat":
        with st.status(
            "Initializing session teardown...", expanded=True
        ) as status:
            st.write("⏳ Flushing localized vector index buffers...")
            time.sleep(0.5)

            # Purge Pinecone namespace
            cleanup_vector_resources()

            st.write("🗑️ Disposing of temporary session variables...")
            time.sleep(0.5)

            st.write("🔒 Creating new contextual environment...")
            time.sleep(0.5)

            status.update(
                label="✨ New Chat Initialized!",
                state="complete",
                expanded=False,
            )
            time.sleep(0.3)

        st.success("🚀 Ready for another financial discussion ✅")

        # Reset session states
        st.session_state.messages = []
        st.session_state.talk_with_ai_count = 0
        st.session_state.embeddings_obj = None
        st.session_state.chat_placeholder = "Ask a financial question... e.g., 'Impacts of war global stock markets'"
        st.session_state.pending_action = None
        st.rerun()

    elif st.session_state.pending_action == "logout":
        with st.status(
            "Initializing session teardown...", expanded=True
        ) as status:
            st.write("⏳ Flushing localized vector index buffers...")
            time.sleep(0.5)

            # Purge Pinecone namespace
            cleanup_vector_resources()

            st.write("🗑️ Disposing of temporary session variables...")
            time.sleep(0.5)

            st.write("🔒 Disconnecting secure API pipelines...")
            time.sleep(0.5)

            status.update(
                label="System Offline: Session Closed Safely",
                state="complete",
                expanded=False,
            )

        st.success("👋 You have been successfully logged out of the terminal.")
        time.sleep(0.5)

        # Clear login state
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.userid = None
        st.session_state.messages = []
        st.session_state.talk_with_ai_count = 0
        st.session_state.embeddings_obj = None
        st.session_state.pending_action = None
        st.session_state.chat_placeholder = "Ask a financial question... e.g., 'Impacts of war global stock markets'"
        st.rerun()






