"""
Agent squad assembled here.

Three agents walk into a bar...
- ResearchAgent orders first, gathers intel
- CopyAgent writes the pickup lines  
- QAAgent makes sure nobody sounds desperate

That's basically how this works.

Now with llm_router - agents don't know which LLM they're using,
and that's exactly how we like it.
"""

from .research_agent import run_research
from .copy_agent import run_copy
from .qa_agent import run_qa

__all__ = [
    "run_research",
    "run_copy",
    "run_qa",
]
