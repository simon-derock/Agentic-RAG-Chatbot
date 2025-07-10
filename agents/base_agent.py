"""Base Agent Class for MCP Communication"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from core.mcp import MCPMessage, message_bus

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.message_bus = message_bus
        
        # Subscribe to message bus
        self.message_bus.subscribe(self.name, self.handle_message)
    
    @abstractmethod
    async def handle_message(self, message: MCPMessage) -> None:
        """Handle incoming MCP messages"""
        pass
    
    async def send_message(self, receiver: str, msg_type, payload: Dict[str, Any], 
                          trace_id: str = None) -> None:
        """Send message to another agent"""
        message = self.message_bus.create_message(
            sender=self.name,
            receiver=receiver,
            msg_type=msg_type,
            payload=payload,
            trace_id=trace_id
        )
        await self.message_bus.send_message(message)
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Simple logging mechanism"""
        print(f"[{level}] {self.name}: {message}")