"""
Research Agent - The corporate detective.

This agent's job is to dig through company websites and find
the juicy bits we can use for personalization. No opinions,
just facts. Like a robot journalist, but less annoying.
"""

from typing import Dict, Any

from app.llm.router import llm_router


def run_research(
    company_name: str,
    website_content: str,
    target_role: str
) -> str:
    """
    Analyze company and extract personalization data.
    
    This is the first agent in the chain. It takes raw website
    content and turns it into structured intel for the copy agent.
    
    Args:
        company_name: Who we're researching (not stalking)
        website_content: The scraped text from their site
        target_role: Who we're emailing (so we know what to focus on)
        
    Returns:
        JSON string with research findings
    """
    prompt = f"""Analyze the following company information and extract key details.

COMPANY: {company_name}
TARGET RECIPIENT ROLE: {target_role}

WEBSITE CONTENT:
{website_content}

YOUR TASK:
1. Identify the company's industry/sector
2. Extract their main value proposition (what they offer and why it matters)
3. Find 3-5 personalization hooks - specific facts that could be referenced in a cold email
4. Write a brief 2-3 sentence company summary

RULES:
- Only state facts found in the content
- No assumptions or opinions
- Personalization hooks must be specific and verifiable
- Focus on details relevant to the target role: {target_role}

OUTPUT FORMAT (JSON only, no markdown):
{{
    "industry": "string",
    "value_proposition": "string",
    "personalization_hooks": ["string", "string", ...],
    "company_summary": "string"
}}

Return ONLY the JSON object, nothing else."""

    # Hit the router - it decides which LLM to use
    response = llm_router.generate(
        task="research",
        prompt=prompt
    )
    
    return response
