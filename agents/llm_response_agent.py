"""LLM Response Agent for Answer Generation"""

from typing import Dict, Any
import google.generativeai as genai
from agents.base_agent import BaseAgent
from core.mcp import MCPMessage, MessageType
from config.settings import get_settings

class LLMResponseAgent(BaseAgent):
    """Agent responsible for generating responses using LLM"""
    
    def __init__(self):
        super().__init__("LLMResponseAgent")
        self.settings = get_settings()
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize Google Gemini LLM"""
        api_key = self.settings.get('GOOGLE_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            self.llm_available = True
            self.log("Gemini LLM initialized")
        else:
            self.llm_available = False
            self.log("No API key provided - using fallback responses", "WARNING")
    
    async def handle_message(self, message: MCPMessage) -> None:
        """Handle incoming messages"""
        try:
            if message.type == MessageType.USER_QUERY:
                await self._process_user_query(message)
            elif message.type == MessageType.RETRIEVAL_RESULT:
                await self._generate_response(message)
            else:
                self.log(f"Unhandled message type: {message.type}", "WARNING")
        except Exception as e:
            self.log(f"Error handling message: {str(e)}", "ERROR")
            await self._send_error_message(message, str(e))
    
    async def _process_user_query(self, message: MCPMessage) -> None:
        """Process user query and request retrieval"""
        payload = message.payload
        query = payload.get('query')
        
        if not query:
            raise ValueError("Missing query in user message")
        
        self.log(f"Processing user query: {query}")
        
        # Request retrieval from RetrievalAgent
        await self.send_message(
            receiver="RetrievalAgent",
            msg_type=MessageType.RETRIEVAL_REQUEST,
            payload={
                "query": query,
                "n_results": 5
            },
            trace_id=message.trace_id
        )
    
    async def _generate_response(self, message: MCPMessage) -> None:
        """Generate response using LLM and retrieved context"""
        payload = message.payload
        query = payload.get('query')
        retrieved_context = payload.get('retrieved_context', [])
        
        self.log(f"Generating response for query with {len(retrieved_context)} context items")
        
        # Generate response
        if self.llm_available:
            response = await self._generate_llm_response(query, retrieved_context)
        else:
            response = self._generate_fallback_response(query, retrieved_context)
        
        # Extract source information
        source_info = []
        for context in retrieved_context:
            source_entry = {"document": context.get('source', 'unknown')}
            
            # Add location information
            if 'page' in context:
                source_entry['page'] = context['page']
            elif 'slide' in context:
                source_entry['slide'] = context['slide']
            elif 'row' in context:
                source_entry['row'] = context['row']
            elif 'paragraph' in context:
                source_entry['paragraph'] = context['paragraph']
            
            source_info.append(source_entry)
        
        # Send final response to UI
        await self.send_message(
            receiver="UI",
            msg_type=MessageType.FINAL_RESPONSE,
            payload={
                "answer": response,
                "source_info": source_info,
                "query": query
            },
            trace_id=message.trace_id
        )
    
    async def _generate_llm_response(self, query: str, context: list) -> str:
        """Generate response using Gemini LLM"""
        # Prepare context text
        context_text = "\n\n".join([
            f"Source: {item.get('source', 'unknown')}\n{item['text']}"
            for item in context
        ])
        
        # Create prompt
        prompt = f"""
Based on the following context from uploaded documents, answer the user's question. 
Be accurate, concise, and cite the sources when possible.

Context:
{context_text}

Question: {query}

Answer:
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.log(f"LLM generation error: {str(e)}", "ERROR")
            return self._generate_fallback_response(query, context)
    
    def _generate_fallback_response(self, query: str, context: list) -> str:
        """Generate fallback response when LLM is not available"""
        if not context:
            return "I couldn't find relevant information in the uploaded documents to answer your question."
        
        # Simple context-based response
        context_snippets = []
        for item in context[:3]:  # Limit to top 3 results
            source = item.get('source', 'unknown')
            text = item['text'][:200] + "..." if len(item['text']) > 200 else item['text']
            context_snippets.append(f"From {source}: {text}")
        
        return f"Based on the uploaded documents, here are the most relevant passages:\n\n" + "\n\n".join(context_snippets)
    
    async def _send_error_message(self, original_message: MCPMessage, error: str) -> None:
        """Send error message to UI"""
        await self.send_message(
            receiver="UI",
            msg_type=MessageType.ERROR,
            payload={
                "error": error,
                "original_message": original_message.to_dict()
            },
            trace_id=original_message.trace_id
        )