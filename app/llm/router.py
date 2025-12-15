"""
LLM Router - One router to rule them all.

Right now: Everything goes to Gemini (fast, cheap, good enough).
Later: Route by task to the best model for each job.

The agents don't know or care which LLM they're talking to.
That's the whole point.

Usage:
    from app.llm.router import llm_router
    
    response = llm_router.generate(task="copy", prompt="Write an email...")
"""

import os
from typing import Literal

import google.generativeai as genai


# Task types we support - add more as needed
TaskType = Literal["research", "copy", "qa"]


class LLMRouter:
    """
    Routes LLM requests to the appropriate provider.
    
    Currently: Gemini handles everything.
    Future: Task-specific routing (Claude for copy, GPT for research, etc.)
    
    Why a class? So we can:
    - Lazy-load API clients
    - Cache connections
    - Add retries/fallbacks later
    - Mock it easily in tests
    """
    
    def __init__(self):
        self._gemini_configured = False
        self._gemini_model = None
        
        # future providers go here
        # self._openai_client = None
        # self._anthropic_client = None
    
    def _setup_gemini(self) -> None:
        """
        Initialize Gemini client.
        
        Lazy loading because:
        1. Don't hit the API until we need to
        2. Easier testing
        3. Faster startup
        """
        if self._gemini_configured:
            return
            
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. "
                "Get one at https://makersuite.google.com/app/apikey"
            )
        
        genai.configure(api_key=api_key)
        
        # Using gemini-2.5-flash - latest flash model, separate quota bucket
        # Verified available: gemini-2.0-flash, gemini-2.0-flash-lite, gemini-2.5-flash
        self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        self._gemini_configured = True
    
    def _call_gemini(self, prompt: str) -> str:
        """
        Send prompt to Gemini, get response.
        
        Nothing fancy, just a clean wrapper.
        """
        self._setup_gemini()
        
        response = self._gemini_model.generate_content(prompt)
        
        # Gemini returns a response object, we just want the text
        return response.text
    
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
        # Right now: Everything goes to Gemini
        # Later: Uncomment the routing below
        # =============================================
        
        # --- PHASE 1: Gemini for all (current) ---
        return self._call_gemini(prompt)
        
        # --- PHASE 2: Task-specific routing (future) ---
        # Uncomment when ready to upgrade:
        #
        # if task == "research":
        #     # Gemini is great at factual summarization
        #     return self._call_gemini(prompt)
        #
        # elif task == "copy":
        #     # Claude is the king of tone and persuasion
        #     return self._call_anthropic(prompt)
        #
        # elif task == "qa":
        #     # Fast model for pattern detection
        #     return self._call_gemini(prompt)
        #
        # else:
        #     # fallback to gemini
        #     return self._call_gemini(prompt)
    
    # =============================================
    # FUTURE PROVIDERS (scaffolding)
    # =============================================
    
    # def _setup_openai(self) -> None:
    #     """Initialize OpenAI client."""
    #     if self._openai_client:
    #         return
    #     from openai import OpenAI
    #     self._openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    #
    # def _call_openai(self, prompt: str, model: str = "gpt-4o") -> str:
    #     """Call OpenAI."""
    #     self._setup_openai()
    #     response = self._openai_client.chat.completions.create(
    #         model=model,
    #         messages=[{"role": "user", "content": prompt}]
    #     )
    #     return response.choices[0].message.content
    
    # def _setup_anthropic(self) -> None:
    #     """Initialize Anthropic client."""
    #     if self._anthropic_client:
    #         return
    #     import anthropic
    #     self._anthropic_client = anthropic.Anthropic(
    #         api_key=os.getenv("ANTHROPIC_API_KEY")
    #     )
    #
    # def _call_anthropic(self, prompt: str) -> str:
    #     """Call Claude."""
    #     self._setup_anthropic()
    #     response = self._anthropic_client.messages.create(
    #         model="claude-3-5-sonnet-20241022",
    #         max_tokens=2048,
    #         messages=[{"role": "user", "content": prompt}]
    #     )
    #     return response.content[0].text


# Global singleton - import this in your agents
# No need to instantiate every time
llm_router = LLMRouter()
