# Codebase RAG Chatbot

![image](https://github.com/user-attachments/assets/ddd4e53a-0f8d-4ff7-995c-40e54e142d29)

## Overview

An advanced retrieval-augmented generation (RAG) system designed to interact with codebases. This application allows users to query code repositories using natural language and receive contextually relevant responses, leveraging the power of Pinecone and Groq's LLM.

## 🔥 Features

* **Codebase Querying**: Use natural language to query your codebase and receive detailed responses.
* **Pinecone Integration**: Efficiently index and search through large codebases using Pinecone's vector database.
* **Groq LLM**: Generate accurate and context-aware responses with Groq's language model.
* **Multi-Repository Support**: Seamlessly switch between different codebases.

## 🚀 Live Demo

Try out the live application here: [Codebase RAG Chatbot](https://codebase.streamlit.app/)

## 💻 Tech Stack

* Python 3.12
* Pinecone
* Groq API
* Sentence Transformers
* GitPython

## 📊 Model Performance

* Efficient indexing and querying of large codebases.
* High accuracy in retrieving relevant code snippets and documentation.

## 🛠️ Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/codebase-rag-chatbot.git
   cd codebase-rag-chatbot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the root directory and add:
   ```
   PINECONE_API_KEY=your_pinecone_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

### Prerequisites

* Python 3.11 or higher
* Pinecone API key
* Groq API key
* Git

## 📁 Project Structure

```
codebase-rag-chatbot/
├── main.py # Main application script
├── ragUtils.py # Utility functions for RAG operations
├── requirements.txt # Project dependencies
├── .env # Environment variables (API keys)
└── README.md # Project documentation
```

## 🔮 Future Improvements

* **Multimodal RAG**: Add support for image uploads when chatting with the codebase.
* **Codebase Selection**: Add a way to select different codebases to chat with.
* **Automated Index Updates**: Add a way to update the Pinecone index when you push any new commits to your repo. This would be done through a webhook that's triggered on each commit, where the codebase is re-embedded and added to Pinecone.
* **Multi-Codebase Chat**: Add a way to chat with multiple codebases at the same time.

## 📝 Blog Post

Read about the development process and technical details in my blog post: [How I Built a System to Interact with Codebases Using RAG and LLMs](#)

## 📫 Contact
- LinkedIn: [Alex Wang](https://www.linkedin.com/in/alexwang-/)
- Twitter: [@imalexwang](https://x.com/imalexwang)
- Blog: [solo diaries](https://imalexwang.substack.com/)
