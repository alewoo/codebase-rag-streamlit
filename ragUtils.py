import os
from pathlib import Path
from typing import List, Dict
from git import Repo
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from openai import OpenAI

SUPPORTED_EXTENSIONS = {'.py', '.js', '.tsx', '.jsx', '.ipynb', '.java',
                       '.cpp', '.ts', '.go', '.rs', '.vue', '.swift', '.c', '.h'}

IGNORED_DIRS = {'node_modules', 'venv', 'env', 'dist', 'build', '.git',
                '__pycache__', '.next', '.vscode', 'vendor'}

class CodebaseRAG:
    def __init__(self, pinecone_api_key: str, groq_api_key: str):
        # Initialize Pinecone
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.pinecone_index = self.pc.Index("codebase-rag")
        
        # Initialize Groq client
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key
        )
        
        # Initialize embeddings model
        self.embeddings_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    def clone_repository(self, repo_url: str, local_path: str) -> str:
        """Clones a GitHub repository to a specified path."""
        # Format the GitHub URL properly
        if not repo_url.startswith("https://"):
            repo_url = f"https://github.com/{repo_url}"
        
        repo_name = repo_url.split("/")[-1]
        repo_path = os.path.join(local_path, repo_name)
        
        # Create the local directory if it doesn't exist
        os.makedirs(local_path, exist_ok=True)
        
        try:
            if not os.path.exists(repo_path):
                Repo.clone_from(repo_url, str(repo_path))
            return str(repo_path)
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")

    def get_file_content(self, file_path: str, repo_path: str) -> Dict:
        """Get content of a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            rel_path = os.path.relpath(file_path, repo_path)
            return {"name": rel_path, "content": content}
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return None

    def process_repository(self, repo_path: str) -> List[Dict]:
        """Process all files in the repository."""
        files_content = []
        for root, _, files in os.walk(repo_path):
            if any(ignored_dir in root for ignored_dir in IGNORED_DIRS):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.splitext(file)[1] in SUPPORTED_EXTENSIONS:
                    file_content = self.get_file_content(file_path, repo_path)
                    if file_content:
                        files_content.append(file_content)
        return files_content

    def index_repository(self, files_content: List[Dict], namespace: str):
        """Index repository content in Pinecone with size limits."""
        MAX_CHUNK_SIZE = 2000  # characters per chunk
        documents = []
        
        for file in files_content:
            # Split content into smaller chunks
            content = file['content']
            chunks = [content[i:i + MAX_CHUNK_SIZE] 
                     for i in range(0, len(content), MAX_CHUNK_SIZE)]
            
            # Create a document for each chunk
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": file['name'],
                        "chunk": i,
                        "total_chunks": len(chunks)
                    }
                )
                documents.append(doc)

        try:
            vectorstore = PineconeVectorStore.from_documents(
                documents=documents,
                embedding=HuggingFaceEmbeddings(),
                index_name="codebase-rag",
                namespace=namespace
            )
            return vectorstore
        except Exception as e:
            raise Exception(f"Failed to index content: {str(e)}")

    def query_codebase(self, query: str, namespace: str) -> str:
        """Query the codebase using RAG."""
        # Create query embedding
        query_embedding = self.embeddings_model.encode(query)
        
        # Get similar contexts from Pinecone
        top_matches = self.pinecone_index.query(
            vector=query_embedding.tolist(),
            top_k=3,  # Reduced from 5 to handle chunks better
            include_metadata=True,
            namespace=namespace
        )
        
        # Extract and combine contexts
        contexts = []
        for item in top_matches['matches']:
            if 'text' in item['metadata']:
                contexts.append(item['metadata']['text'])
        
        # Create augmented query with size limit
        context_text = "\n\n-------\n\n".join(contexts[:3])  # Limit context size
        augmented_query = f"<CONTEXT>\n{context_text}\n-------\n</CONTEXT>\n\n\nMY QUESTION:\n{query}"
        
        # Get LLM response
        system_prompt = """You are a Senior Software Engineer, specializing in TypeScript.
        Answer any questions I have about the codebase, based on the code provided. Always consider all of the context provided when forming a response."""
        
        llm_response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": augmented_query}
            ]
        )
        
        return llm_response.choices[0].message.content