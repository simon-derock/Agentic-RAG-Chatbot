"""Ingestion Agent for Document Processing"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from core.mcp import MCPMessage, MessageType
from core.document_parser import DocumentParser

class IngestionAgent(BaseAgent):
    """Agent responsible for document ingestion and parsing"""
    
    def __init__(self):
        super().__init__("IngestionAgent")
        self.parser = DocumentParser()
    
    async def handle_message(self, message: MCPMessage) -> None:
        """Handle incoming messages"""
        try:
            if message.type == MessageType.DOC_UPLOADED:
                await self._process_document(message)
            else:
                self.log(f"Unhandled message type: {message.type}", "WARNING")
        except Exception as e:
            self.log(f"Error handling message: {str(e)}", "ERROR")
            await self._send_error_message(message, str(e))
    
    async def _process_document(self, message: MCPMessage) -> None:
        """Process uploaded document"""
        payload = message.payload
        file_name = payload.get('file_name')
        file_data = payload.get('file_data')
        
        if not file_name or not file_data:
            raise ValueError("Missing file_name or file_data in payload")
        
        self.log(f"Processing document: {file_name}")
        
        # Parse document into chunks
        chunks = self.parser.parse_document(file_data, file_name)
        
        self.log(f"Extracted {len(chunks)} chunks from {file_name}")
        
        # Send chunks to RetrievalAgent
        await self.send_message(
            receiver="RetrievalAgent",
            msg_type=MessageType.DOC_INGESTED,
            payload={
                "chunks": chunks,
                "file_name": file_name,
                "total_chunks": len(chunks)
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