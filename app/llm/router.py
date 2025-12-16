"""
LLM Router - One router to rule them all.

Right now: Everything goes to Mistral (fast, cheap, great quality).
Later: Route by task to the best model for each job.

The agents don't know or care which LLM they're talking to.
That's the whole point.

Usage:
    from app.llm.router import llm_router
    
    response = llm_router.generate(task="copy", prompt="Write an email...")
"""

import os
from typing import Literal

from mistralai import Mistral


# Task types we support - add more as needed
TaskType = Literal["research", "copy", "qa"]


class LLMRouter:
    """
    Routes LLM requests to the appropriate provider.
    
    Currently: Mistral handles everything.
    Future: Task-specific routing (Claude for copy, GPT for research, etc.)
    
    Why a class? So we can:
    - Lazy-load API clients
    - Cache connections
    - Add retries/fallbacks later
    - Mock it easily in tests
    """
    
    def __init__(self):
        self._mistral_client = None
        self._mistral_configured = False
        
        # future providers go here
        # self._openai_client = None
        # self._anthropic_client = None
    
    def _setup_mistral(self) -> None:
        """
        Initialize Mistral client.
        
        Lazy loading because:
        1. Don't hit the API until we need to
        2. Easier testing
        3. Faster startup
        """
        if self._mistral_configured:
            return
            
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError(
                "MISTRAL_API_KEY not set. "
                "Get one at https://console.mistral.ai/api-keys"
            )
        
        self._mistral_client = Mistral(api_key=api_key)
        self._mistral_configured = True
    
    def _call_mistral(self, prompt: str) -> str:
        """
        Send prompt to Mistral, get response.
        
        Using mistral-small-latest - fast, cheap, great for structured output.
        Other options: mistral-medium-latest, mistral-large-latest
        """
        self._setup_mistral()
        
        response = self._mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Mistral returns a response object, we just want the text
        return response.choices[0].message.content
    
    def generate(self, task: TaskType, prompt: str) -> str:
        """
        Generate a response for the given task.
        
        This is THE method agents call. One interface, any backend.
        
        Args:
            task: What kind of work this is ("research", "copy", "qa")
            prompt: The actual prompt to send
            
        Returns:
            LLM response text
            
        Example:
            >>> response = llm_router.generate(
            ...     task="copy",
            ...     prompt="Write a cold email for Acme Corp..."
            ... )
        """
        # =============================================
        # ROUTING LOGIC
        # 
        # Right now: Everything goes to Mistral
        # Later: Uncomment the routing below
        # =============================================
        
        # --- PHASE 1: Mistral for all (current) ---
        return self._call_mistral(prompt)


# Global singleton - import this in your agents
# No need to instantiate every time
llm_router = LLMRouter()
