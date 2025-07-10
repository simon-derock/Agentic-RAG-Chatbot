"""Streamlit UI for Agentic RAG Chatbot"""

import streamlit as st
import asyncio
import uuid
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from core.mcp import MCPMessage, MessageType, message_bus

class UIAgent(BaseAgent):
    """UI Agent for handling Streamlit interface"""
    
    def __init__(self):
        super().__init__("UI")
        self.responses = {}
        self.errors = {}
    
    async def handle_message(self, message: MCPMessage) -> None:
        """Handle incoming messages from other agents"""
        trace_id = message.trace_id
        
        if message.type == MessageType.FINAL_RESPONSE:
            self.responses[trace_id] = message.payload
        elif message.type == MessageType.ERROR:
            self.errors[trace_id] = message.payload
    
    async def upload_document(self, file_name: str, file_data: bytes) -> str:
        """Upload document to ingestion agent"""
        trace_id = str(uuid.uuid4())
        
        await self.send_message(
            receiver="IngestionAgent",
            msg_type=MessageType.DOC_UPLOADED,
            payload={
                "file_name": file_name,
                "file_data": file_data
            },
            trace_id=trace_id
        )
        
        return trace_id
    
    async def ask_question(self, query: str) -> str:
        """Send user query to LLM response agent"""
        trace_id = str(uuid.uuid4())
        
        await self.send_message(
            receiver="LLMResponseAgent",
            msg_type=MessageType.USER_QUERY,
            payload={
                "query": query
            },
            trace_id=trace_id
        )
        
        return trace_id
    
    def get_response(self, trace_id: str) -> Dict[str, Any]:
        """Get response for a trace ID"""
        return self.responses.get(trace_id)
    
    def get_error(self, trace_id: str) -> Dict[str, Any]:
        """Get error for a trace ID"""
        return self.errors.get(trace_id)

class StreamlitApp:
    """Main Streamlit application"""
    
    def __init__(self):
        self.ui_agent = UIAgent()
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize Streamlit session state"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'agents_initialized' not in st.session_state:
            st.session_state.agents_initialized = False
    
    def initialize_agents(self):
        """Initialize all agents"""
        if not st.session_state.agents_initialized:
            from agents.ingestion_agent import IngestionAgent
            from agents.retrieval_agent import RetrievalAgent
            from agents.llm_response_agent import LLMResponseAgent
            
            # Create agents
            st.session_state.ingestion_agent = IngestionAgent()
            st.session_state.retrieval_agent = RetrievalAgent()
            st.session_state.llm_response_agent = LLMResponseAgent()
            
            st.session_state.agents_initialized = True
    
    def render_sidebar(self):
        """Render sidebar with file upload and settings"""
        st.sidebar.title("📁 Document Upload")
        
        uploaded_files = st.sidebar.file_uploader(
            "Choose files",
            type=['pdf', 'pptx', 'csv', 'docx', 'txt', 'md'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in [f['name'] for f in st.session_state.uploaded_files]:
                    # Process file upload
                    file_data = uploaded_file.read()
                    
                    # Upload to ingestion agent
                    trace_id = asyncio.run(self.ui_agent.upload_document(
                        uploaded_file.name, file_data
                    ))
                    
                    # Add to session state
                    st.session_state.uploaded_files.append({
                        'name': uploaded_file.name,
                        'size': len(file_data),
                        'trace_id': trace_id
                    })
                    
                    st.sidebar.success(f"✅ {uploaded_file.name} uploaded")
        
        # Display uploaded files
        if st.session_state.uploaded_files:
            st.sidebar.subheader("📄 Uploaded Files")
            for file_info in st.session_state.uploaded_files:
                st.sidebar.text(f"• {file_info['name']}")
        
        # Settings
        st.sidebar.subheader("⚙️ Settings")
        if st.sidebar.button("Clear All Documents"):
            st.session_state.uploaded_files = []
            st.session_state.retrieval_agent.clear_store()
            st.sidebar.success("Documents cleared")
    
    def render_chat_interface(self):
        """Render main chat interface"""
        st.title("🤖 Agentic RAG Chatbot")
        st.markdown("Upload documents and ask questions about their content!")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display sources if available
                if message.get("sources"):
                    with st.expander("📚 Sources"):
                        for source in message["sources"]:
                            source_text = f"**{source['document']}**"
                            if 'page' in source:
                                source_text += f" (Page {source['page']})"
                            elif 'slide' in source:
                                source_text += f" (Slide {source['slide']})"
                            elif 'row' in source:
                                source_text += f" (Row {source['row']})"
                            elif 'paragraph' in source:
                                source_text += f" (Paragraph {source['paragraph']})"
                            
                            st.markdown(source_text)
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process question
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    trace_id = asyncio.run(self.ui_agent.ask_question(prompt))
                    
                    # Wait for response
                    response = None
                    error = None
                    max_attempts = 50
                    attempts = 0
                    
                    while attempts < max_attempts:
                        response = self.ui_agent.get_response(trace_id)
                        error = self.ui_agent.get_error(trace_id)
                        
                        if response or error:
                            break
                        
                        asyncio.run(asyncio.sleep(0.1))
                        attempts += 1
                    
                    if error:
                        error_msg = f"❌ Error: {error.get('error', 'Unknown error')}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })
                    elif response:
                        answer = response.get('answer', 'No answer generated')
                        sources = response.get('source_info', [])
                        
                        st.markdown(answer)
                        
                        # Display sources
                        if sources:
                            with st.expander("📚 Sources"):
                                for source in sources:
                                    source_text = f"**{source['document']}**"
                                    if 'page' in source:
                                        source_text += f" (Page {source['page']})"
                                    elif 'slide' in source:
                                        source_text += f" (Slide {source['slide']})"
                                    elif 'row' in source:
                                        source_text += f" (Row {source['row']})"
                                    elif 'paragraph' in source:
                                        source_text += f" (Paragraph {source['paragraph']})"
                                    
                                    st.markdown(source_text)
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer,
                            "sources": sources
                        })
                    else:
                        timeout_msg = "⏰ Request timed out. Please try again."
                        st.error(timeout_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": timeout_msg
                        })
    
    def run(self):
        """Run the Streamlit application"""
        st.set_page_config(
            page_title="Agentic RAG Chatbot",
            page_icon="🤖",
            layout="wide"
        )
        
        self.initialize_agents()
        
        self.render_sidebar()
        self.render_chat_interface()

# Create and run the app
if __name__ == "__main__":
    app = StreamlitApp()
    app.run()