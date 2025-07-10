# Agentic RAG Chatbot

This project implements a sophisticated, multi-agent Retrieval-Augmented Generation (RAG) chatbot. It allows users to upload various document types and ask questions about their content. The chatbot leverages a powerful agentic architecture, where specialized agents collaborate to ingest, retrieve, and generate responses, all orchestrated through a central message bus.

## ✨ Features

- **Multi-Format Document Support:** Upload and chat with PDFs, PowerPoints, CSVs, Word documents, Markdown, and plain text files.
- **Retrieval-Augmented Generation (RAG):** Answers are generated based on the content of your uploaded documents, ensuring relevance and accuracy.
- **Agentic Architecture:** A modular system where different agents handle specific tasks (ingestion, retrieval, LLM response), making the system scalable and maintainable.
- **Vector-Based Semantic Search:** Utilizes `ChromaDB` and `Sentence-Transformers` for efficient and accurate semantic search across your documents.
- **Google Gemini Integration:** Powered by Google's `gemini-1.5-flash-latest` model for high-quality response generation.
- **Interactive UI:** A user-friendly web interface built with `Streamlit` for easy document management and conversation.

## 🏗️ Architecture Overview

The chatbot operates on a **Model Context Protocol (MCP)**, an internal message bus that facilitates communication between specialized agents.

1.  **UI Agent (`UIAgent`):** Manages the Streamlit front end, handling user interactions like file uploads and queries.
2.  **Ingestion Agent (`IngestionAgent`):** Receives documents from the UI, parses them using `DocumentParser`, and sends the extracted text chunks to the Retrieval Agent.
3.  **Retrieval Agent (`RetrievalAgent`):** Manages the `VectorStore`. It receives text chunks, creates vector embeddings, and stores them in ChromaDB. It also handles search queries to find relevant context.
4.  **LLM Response Agent (`LLMResponseAgent`):** Orchestrates the response generation. It requests relevant context from the Retrieval Agent, constructs a detailed prompt, and queries the Google Gemini LLM to generate a final answer.

![Architecture Diagram](https://i.imgur.com/example.png)  <!-- Placeholder for a diagram -->

---

## 🚀 Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

- Python 3.10 or higher
- `pip` package manager
- `git` (optional, for cloning)

### 2. Clone the Repository

First, get the project files onto your local machine.

```bash
git clone https://github.com/your-username/agentic-rag-chatbot.git
cd agentic-rag-chatbot
```

### 3. Create a Python Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with other Python projects.

**On macOS/Linux:**
```bash
python3 -m venv virtual_container
```

**On Windows:**
```bash
python -m venv virtual_container
```

### 4. Activate the Virtual Environment

Before installing dependencies, you must activate the environment.

**On macOS/Linux:**
```bash
source virtual_container/bin/activate
```

**On Windows:**
```bash
.\virtual_container\Scripts\activate
```

Your terminal prompt should now be prefixed with `(virtual_container)`, indicating that the virtual environment is active.

### 5. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 6. Set Up Google API Key

This project uses the Google Gemini API for language model capabilities. You need to provide an API key as an environment variable.

1.  Obtain a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Set the environment variable.

**On macOS/Linux:**
```bash
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```
To make this permanent, add the line above to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`).

**On Windows (Command Prompt):**
```bash
set GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

**On Windows (PowerShell):**
```bash
$env:GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

> **Note:** If you do not provide an API key, the application will run in a fallback mode, providing responses based on direct context snippets instead of a generated summary.

### 7. Run the Application

Once the setup is complete, you can start the Streamlit application.

```bash
streamlit run ui/streamlit_app.py
```

The application will automatically open in your web browser, typically at `http://localhost:8501`.

---

## 📖 How to Use

1.  **Upload Documents:** Use the sidebar to upload one or more supported files (`pdf`, `pptx`, `csv`, `docx`, `txt`, `md`).
2.  **Wait for Processing:** The files will be processed and ingested into the vector store. You'll see a success message for each file.
3.  **Ask Questions:** Type your questions into the chat input at the bottom of the page and press Enter.
4.  **View Responses:** The chatbot will respond with an answer based on the information in your documents.
5.  **Check Sources:** You can expand the "Sources" section below each answer to see which documents (and specific parts) were used to generate the response.

## Project Structure

```
agentic-rag-chatbot/
├── requirements.txt
├── main.py
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── ingestion_agent.py
│   ├── retrieval_agent.py
│   └── llm_response_agent.py
├── core/
│   ├── __init__.py
│   ├── mcp.py
│   ├── document_parser.py
│   └── vector_store.py
├── ui/
│   ├── __init__.py
│   └── streamlit_app.py
└── config/
    ├── __init__.py
    └── settings.py
```

## ⚙️ Key Dependencies

- **`streamlit`**: For creating the interactive web UI.
- **`chromadb`**: The vector database for storing and searching document embeddings.
- **`sentence-transformers`**: For generating high-quality semantic embeddings of text.
- **`google-generativeai`**: The official Python client for the Google Gemini API.
- **`PyPDF2`, `python-pptx`, `pandas`, `python-docx`**: For parsing various document formats.
