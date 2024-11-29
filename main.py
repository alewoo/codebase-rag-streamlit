import streamlit as st
from ragUtils import CodebaseRAG
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_repo' not in st.session_state:
    st.session_state.current_repo = None

# Verify API keys and initialize RAG
if not pinecone_api_key or not groq_api_key:
    st.error("⚠️ API keys not found in environment variables. Please check your .env file.")
else:
    if 'rag' not in st.session_state:
        try:
            st.session_state.rag = CodebaseRAG(pinecone_api_key, groq_api_key)
        except Exception as e:
            st.error(f"Error initializing RAG: {str(e)}")

# App title
st.title("Codebase Chat")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Repository URL input
    repo_url = st.text_input("GitHub Repository URL")
    
    # Initialize button
    if st.button("Initialize Repository"):
        if not st.session_state.rag:
            st.error("⚠️ RAG system not initialized. Please check your API keys.")
        elif repo_url:
            try:
                # Clone and process repository
                repo_path = st.session_state.rag.clone_repository(repo_url, "./repos")
                files_content = st.session_state.rag.process_repository(repo_path)
                
                # Index repository
                namespace = repo_url
                st.session_state.rag.index_repository(files_content, namespace)
                st.session_state.current_repo = repo_url
                
                st.success("Repository initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing repository: {str(e)}")
        else:
            st.error("Please provide a repository URL")

# Chat interface
if st.session_state.rag and st.session_state.current_repo:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about the codebase"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.rag.query_codebase(prompt, st.session_state.current_repo)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Please initialize a repository using the sidebar configuration.")