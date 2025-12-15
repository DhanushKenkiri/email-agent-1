"""
QA Agent - The spam police we all need.

This agent looks at our beautifully crafted emails and asks the 
hard question: "Would this annoy me if it landed in MY inbox?"

It checks for all the classic mistakes that make emails go 
straight to spam/trash/eternal-unread-purgatory.

Does NOT rewrite anything - just judges silently (like your cat).
"""

from app.llm.router import llm_router


def run_qa(copy_output: str) -> str:
    """
    Analyze emails for spam risk.
    
    The QA agent doesn't fix anything - it just tells you
    if your emails are going to get flagged. Like a friend
    reviewing your dating profile before you post it.
    
    Args:
        copy_output: The emails from the copy agent (JSON string)
        
    Returns:
        JSON string with spam analysis
    """
    prompt = f"""Analyze the following cold emails for spam risk.

EMAILS TO ANALYZE:
{copy_output}

SPAM RISK SIGNALS TO CHECK:

1. SALES PHRASE OVERUSE (check for):
   - "Revolutionary", "Game-changing", "Best-in-class"
   - "Act now", "Limited time", "Don't miss out"
   - "Guaranteed", "Risk-free", "No obligation"
   - Multiple value claims without proof

2. URGENCY SIGNALS (check for):
   - Artificial deadlines
   - Pressure tactics
   - FOMO language
   - Multiple CTAs

3. PERSONALIZATION QUALITY (check for):
   - Generic compliments ("I love what you're doing")
   - Name-only personalization
   - Obvious template language
   - Mismatched tone

4. FORMAT ISSUES (check for):
   - ALL CAPS words
   - Emojis present
   - Exclamation marks present
   - Excessive length

SCORING CRITERIA:
- LOW: 0-1 minor issues, emails feel genuine and targeted
- MEDIUM: 2-3 issues, some templated feel but acceptable
- HIGH: 4+ issues, likely to trigger spam filters or annoy recipient

YOUR TASK:
1. Count and list all risk factors found
2. Assign a spam_risk_score: "low", "medium", or "high"
3. Write brief analysis notes

DO NOT:
- Suggest rewrites
- Give opinions on content quality
- Change any email text

OUTPUT FORMAT (JSON only, no markdown):
{{
    "spam_risk_score": "low" | "medium" | "high",
    "risk_factors": ["factor1", "factor2", ...],
    "analysis_notes": "string"
}}

Return ONLY the JSON object, nothing else."""

    # QA can use a fast model - just pattern matching
    response = llm_router.generate(
        task="qa",
        prompt=prompt
    )
    
    return response
