"""
Copy Agent - The wordsmith who doesn't use exclamation marks.

This agent writes cold emails that people might actually read.
No "AMAZING OPPORTUNITY!!!" nonsense. Just clean, personalized
copy that respects the recipient's intelligence (and inbox).

Fun fact: the average cold email gets 3 seconds of attention.
Let's make those seconds count.
"""

from typing import Literal

from app.llm.router import llm_router


# Tone guidelines - what each vibe actually means
TONE_GUIDELINES = {
    "professional": "Formal, respectful, business-appropriate. Use proper titles.",
    "casual": "Friendly but not unprofessional. First-name basis. Conversational.",
    "founder": "Direct, founder-to-founder. Mention building/shipping. No fluff."
}


def run_copy(
    company_name: str,
    target_role: str,
    product_description: str,
    outreach_goal: str,
    tone: Literal["professional", "casual", "founder"],
    research_output: str
) -> str:
    """
    Generate cold outreach emails based on research.
    
    Takes the intel from research agent and crafts actual emails.
    3 subject lines, 1 primary email, 1 follow-up.
    
    Args:
        company_name: The company we're pitching to
        target_role: Their job title (VP of Whatever)
        product_description: What we're selling (hopefully something good)
        outreach_goal: What we want them to do (usually "take my meeting")
        tone: How to sound - professional/casual/founder
        research_output: Intel from the research agent (JSON string)
        
    Returns:
        JSON string with emails and subject lines
    """
    tone_guide = TONE_GUIDELINES.get(tone, TONE_GUIDELINES["professional"])
    
    prompt = f"""Write cold outreach emails based on the research provided.

CONTEXT:
- Company: {company_name}
- Recipient Role: {target_role}
- Your Product: {product_description}
- Goal: {outreach_goal}
- Tone: {tone} - {tone_guide}

RESEARCH DATA:
{research_output}

DELIVERABLES:

1. THREE SUBJECT LINES
   - Under 50 characters each
   - No clickbait
   - Reference company or role when possible

2. PRIMARY EMAIL
   - Maximum 120 words
   - Open with personalization from research
   - Connect their situation to your product
   - End with clear CTA related to: {outreach_goal}
   
3. FOLLOW-UP EMAIL
   - Maximum 120 words
   - Reference the first email
   - Add new value or angle
   - Slightly softer CTA

STRICT RULES:
- ZERO emojis
- ZERO exclamation marks
- No "I hope this email finds you well"
- No "Just following up"
- No "Reaching out because"
- Last sentence MUST be the call-to-action

OUTPUT FORMAT (JSON only, no markdown):
{{
    "subject_lines": ["line1", "line2", "line3"],
    "primary_email": "string",
    "follow_up_email": "string"
}}

Return ONLY the JSON object, nothing else."""

    # Route to the copy-specialized LLM (or Gemini for now)
    response = llm_router.generate(
        task="copy",
        prompt=prompt
    )
    
    return response
