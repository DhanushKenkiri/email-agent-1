"""
Crew Orchestration - Where the magic happens.

This is the conductor of our little AI orchestra:
1. Research Agent plays first (gathering intel)
2. Copy Agent comes in (writing the emails)  
3. QA Agent finishes (making sure we don't sound desperate)

Each agent does ONE thing well and passes the baton.
No freelancing, no improv. Structured chaos.

IMPORTANT: This file does NOT import any LLM libraries.
Agents handle their own LLM calls via the router.
This is pure orchestration only.
"""

import json
import re

from .agents import run_research, run_copy, run_qa
from .schemas import OutreachInput, OutreachOutput, ResearchOutput, CopyOutput, QAOutput
from .utils.web_scraper import WebScraper, ScraperError


class OutreachCrew:
    """
    The mastermind behind cold email generation.
    
    Takes company info in, spits personalized emails out.
    It's like a factory, but for words. A word factory.
    Actually that sounds dystopian. Let's just call it an "agent crew."
    """
    
    def __init__(self):
        self.scraper = WebScraper()  # our window to the corporate web
    
    def run(self, input_data: OutreachInput) -> OutreachOutput:
        """
        Run the whole shebang.
        
        This is where we chain all three agents together and hope
        they play nice. Spoiler: they usually do.
        
        Args:
            input_data: Everything we need to write great emails
            
        Returns:
            Shiny structured output with emails and spam score
            
        Raises:
            ScraperError: Website ghosted us
            ValueError: Agent said something we couldn't parse (rude)
        """
        
        # ============================================
        # STEP 0: Grab the website content
        # (can't personalize what we can't see)
        # ============================================
        website_content = self.scraper.fetch_page(str(input_data.company_website))
        
        # ============================================
        # STEP 1: Research Agent does its thing
        # ============================================
        research_result = run_research(
            company_name=input_data.company_name,
            website_content=website_content,
            target_role=input_data.target_role
        )
        
        research_output = self._parse_json_output(research_result, "research")
        
        # make sure research agent didn't go off-script
        research_validated = ResearchOutput(**research_output)
        
        # ============================================
        # STEP 2: Copy Agent writes the actual emails
        # ============================================
        copy_result = run_copy(
            company_name=input_data.company_name,
            target_role=input_data.target_role,
            product_description=input_data.product_description,
            outreach_goal=input_data.outreach_goal,
            tone=input_data.tone,
            research_output=json.dumps(research_output, indent=2)
        )
        
        copy_output = self._parse_json_output(copy_result, "copy")
        
        # validate the copywriter didn't get creative with the schema
        copy_validated = CopyOutput(**copy_output)
        
        # ============================================
        # STEP 3: QA Agent judges everything
        # ============================================
        qa_result = run_qa(
            copy_output=json.dumps(copy_output, indent=2)
        )
        
        qa_output = self._parse_json_output(qa_result, "qa")
        
        # QA agent better have followed the rules
        qa_validated = QAOutput(**qa_output)
        
        # ============================================
        # FINAL: Package it all up nicely
        # ============================================
        return OutreachOutput(
            subject_lines=copy_validated.subject_lines,
            primary_email=copy_validated.primary_email,
            follow_up_email=copy_validated.follow_up_email,
            personalization_points=research_validated.personalization_hooks,
            spam_risk_score=qa_validated.spam_risk_score
        )
    
    def _parse_json_output(self, raw_output: str, stage: str) -> dict:
        """
        Extract JSON from whatever mess the agent returned.
        
        LLMs love wrapping JSON in markdown code blocks, adding
        commentary, or just being generally unhelpful with formatting.
        This function deals with all that nonsense.
        
        Args:
            raw_output: The agent's raw response (could be anything tbh)
            stage: Which agent this came from (for error messages)
            
        Returns:
            Clean parsed dictionary
            
        Raises:
            ValueError: If we really can't find valid JSON in there
        """
        # first, check if they wrapped it in markdown code blocks
        # (thanks ChatGPT for teaching everyone this habit)
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_output, re.DOTALL)
        if json_match:
            raw_output = json_match.group(1)
        
        # still no luck? try to find a JSON object anywhere in there
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_output, re.DOTALL)
        if json_match:
            raw_output = json_match.group(0)
        
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError as e:
            # welp, agent really didn't follow instructions
            raise ValueError(f"Failed to parse {stage} agent output as JSON: {e}\nRaw: {raw_output[:200]}...")
