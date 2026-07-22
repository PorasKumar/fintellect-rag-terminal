import streamlit as st
import uuid
import time
import logging
# Mute Streamlit's loud internal file-watcher tracking logs
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)


st.set_page_config(page_title="Financial RAG Terminal", layout="wide")

glass_css = """
<style>
    /* ==========================================================================
       1. GLOBAL DARK THEME & BASE STYLES
       ========================================================================== */
    .stApp {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
    }

    /* Force all text inputs, textareas, and select boxes to stay dark */
    div[data-baseweb="input"], 
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"],
    .stTextInput > div > div,
    .stTextArea > div > div {
        background-color: #262730 !important;
        color: #FAFAFA !important;
        border-color: #444444 !important;
        border-radius: 8px !important;
    }

    /* Target inner input fields for text color and placeholder contrast */
    input, textarea {
        color: #FAFAFA !important;
        -webkit-text-fill-color: #FAFAFA !important;
    }

    ::placeholder {
        color: #A0AAB2 !important;
        opacity: 1 !important;
    }

    /* Fix Chrome/Safari mobile auto-fill turning inputs white */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus,
    textarea:-webkit-autofill {
        -webkit-text-fill-color: #FAFAFA !important;
        -webkit-box-shadow: 0 0 0px 1000px #262730 inset !important;
        transition: background-color 5000s ease-in-out 0s;
    }

    /* Header & Title Styling */
    h1, h2, h3, h4, h5, h6, span, label {
        color: #FAFAFA !important;
    }

    /* Sidebar Background & Inputs */
    [data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D !important;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #262730 !important;
        color: #FAFAFA !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton > button:hover {
        background-color: #4CAF50 !important;
        color: #FFFFFF !important;
        border-color: #4CAF50 !important;
    }

    /* Streamlit Native Chat Input Styling */
    .stChatInputContainer {
        background-color: #262730 !important;
        border-color: #444444 !important;
        border-radius: 12px !important;
    }

    /* ==========================================================================
       2. MOBILE RESPONSIVE MEDIA QUERIES (Screen width <= 768px)
       ========================================================================== */
    @media (max-width: 768px) {
        /* Reduce overall container padding so content fits comfortably */
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 5rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }

        /* Force multi-column layouts (st.columns) to stack vertically on phone screens */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 0.5rem !important;
        }

        /* Scale down large headings for smaller mobile displays */
        h1 {
            font-size: 1.6rem !important;
            line-height: 1.2 !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }

        /* Full-width buttons on mobile for easier touch targets */
        .stButton > button {
            width: 100% !important;
            font-size: 16px !important; /* Prevents auto-zoom on iOS Safari */
            padding: 10px 0 !important;
        }

        /* Floating chat bar padding at bottom of mobile viewports */
        .stChatInput {
            bottom: 12px !important;
        }

        /* Prevent side overflow on code snippets and tables */
        .stCodeBlock, pre {
            max-width: 100% !important;
            overflow-x: auto !important;
        }
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






