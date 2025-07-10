"""Retrieval Agent for Vector Search Operations"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from core.mcp import MCPMessage, MessageType
from core.vector_store import VectorStore

class RetrievalAgent(BaseAgent):
    """Agent responsible for vector storage and retrieval"""
    
    def __init__(self):
        super().__init__("RetrievalAgent")
        self.vector_store = VectorStore()
    
    async def handle_message(self, message: MCPMessage) -> None:
        """Handle incoming messages"""
        try:
            if message.type == MessageType.DOC_INGESTED:
                await self._ingest_chunks(message)
            elif message.type == MessageType.RETRIEVAL_REQUEST:
                await self._perform_retrieval(message)
            else:
                self.log(f"Unhandled message type: {message.type}", "WARNING")
        except Exception as e:
            self.log(f"Error handling message: {str(e)}", "ERROR")
            await self._send_error_message(message, str(e))
    
    async def _ingest_chunks(self, message: MCPMessage) -> None:
        """Ingest document chunks into vector store"""
        payload = message.payload
        chunks = payload.get('chunks', [])
        file_name = payload.get('file_name')
        
        self.log(f"Ingesting {len(chunks)} chunks from {file_name}")
        
        # Add chunks to vector store
        self.vector_store.add_documents(chunks)
        
        # Log statistics
        stats = self.vector_store.get_collection_stats()
        self.log(f"Vector store now contains {stats['total_documents']} documents")
    
    async def _perform_retrieval(self, message: MCPMessage) -> None:
        """Perform semantic search and return results"""
        payload = message.payload
        query = payload.get('query')
        n_results = payload.get('n_results', 5)
        
        if not query:
            raise ValueError("Missing query in retrieval request")
        
        self.log(f"Performing retrieval for query: {query}")
        
        # Search vector store
        results = self.vector_store.search(query, n_results)
        
        self.log(f"Found {len(results)} relevant chunks")
        
        # Format context for LLM
        retrieved_context = []
        for result in results:
            context_item = {
                "text": result['text'],
                "source": result.get('source', 'unknown'),
                "score": result.get('score', 0.0)
            }
            
            # Add location metadata based on document type
            if result.get('type') == 'pdf':
                context_item['page'] = result.get('page')
            elif result.get('type') == 'pptx':
                context_item['slide'] = result.get('slide')
            elif result.get('type') == 'csv':
                context_item['row'] = result.get('row')
            elif result.get('type') in ['docx', 'txt', 'md']:
                context_item['paragraph'] = result.get('paragraph')
            
            retrieved_context.append(context_item)
        
        # Send results to LLMResponseAgent
        await self.send_message(
            receiver="LLMResponseAgent",
            msg_type=MessageType.RETRIEVAL_RESULT,
            payload={
                "retrieved_context": retrieved_context,
                "query": query,
                "total_results": len(results)
            },
            trace_id=message.trace_id
        )
    
    async def _send_error_message(self, original_message: MCPMessage, error: str) -> None:
        """Send error message back to sender"""
        await self.send_message(
            receiver=original_message.sender,
            msg_type=MessageType.ERROR,
            payload={
                "error": error,
                "original_message": original_message.to_dict()
            },
            trace_id=original_message.trace_id
        )
    
    def clear_store(self) -> None:
        """Clear all documents from vector store"""
        self.vector_store.clear()
        self.log("Vector store cleared")