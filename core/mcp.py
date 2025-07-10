"""Model Context Protocol (MCP) Implementation for Agent Communication"""

import json
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from collections import defaultdict

class MessageType(Enum):
    DOC_UPLOADED = "DOC_UPLOADED"
    DOC_INGESTED = "DOC_INGESTED"
    USER_QUERY = "USER_QUERY"
    RETRIEVAL_REQUEST = "RETRIEVAL_REQUEST"
    RETRIEVAL_RESULT = "RETRIEVAL_RESULT"
    FINAL_RESPONSE = "FINAL_RESPONSE"
    ERROR = "ERROR"

@dataclass
class MCPMessage:
    sender: str
    receiver: str
    type: MessageType
    trace_id: str
    payload: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type.value,
            "trace_id": self.trace_id,
            "payload": self.payload
        }

class MCPMessageBus:
    """In-memory message bus for agent communication"""
    
    def __init__(self):
        self._subscribers = defaultdict(list)
        self._message_queue = asyncio.Queue()
        self._handlers = {}
        
    def subscribe(self, agent_name: str, handler_func):
        """Subscribe an agent to receive messages"""
        self._subscribers[agent_name].append(handler_func)
        self._handlers[agent_name] = handler_func
    
    async def send_message(self, message: MCPMessage):
        """Send message to target agent"""
        await self._message_queue.put(message)
        
        # Direct delivery to handler
        if message.receiver in self._handlers:
            handler = self._handlers[message.receiver]
            await handler(message)
    
    def create_message(self, sender: str, receiver: str, msg_type: MessageType, 
                      payload: Dict[str, Any], trace_id: Optional[str] = None) -> MCPMessage:
        """Create standardized MCP message"""
        return MCPMessage(
            sender=sender,
            receiver=receiver,
            type=msg_type,
            trace_id=trace_id or str(uuid.uuid4()),
            payload=payload
        )

# Global message bus instance
message_bus = MCPMessageBus()