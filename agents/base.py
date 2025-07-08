from typing import Dict, Optional, AsyncGenerator, List

class Agent:
    """Base Agent class that all specialized agents should inherit from"""
    
    def __init__(self, name, agent_id, **kwargs):
        self.name = name
        self.agent_id = agent_id
        self.description = kwargs.get("description", "")
        
    async def generate_response(self, messages, **kwargs):
        """Generate a non-streaming response"""
        return {
            "role": "assistant",
            "content": f"This is a mock response from {self.agent_id}",
        }
        
    async def generate_streaming_response(self, messages, **kwargs) -> AsyncGenerator[Dict, None]:
        """Generate a streaming response"""
        response_text = f"This is a streaming response from {self.agent_id}."
        
        # Simulate streaming in small chunks
        for i in range(0, len(response_text), 5):
            chunk = response_text[i:i+5]
            yield {"content": chunk, "done": False}
            
        # Send the final chunk
        yield {"content": "", "done": True} 