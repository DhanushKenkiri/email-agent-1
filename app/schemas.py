"""
Pydantic schemas - because raw dicts are for people who enjoy suffering.

These models keep our API honest. If someone sends garbage in,
Pydantic yells at them so we don't have to.
"""

from typing import List, Literal
from pydantic import BaseModel, HttpUrl, Field, field_validator


class OutreachInput(BaseModel):
    """
    What we need to generate cold emails.
    
    Pro tip: garbage in = garbage out. Be specific with your inputs
    or don't blame the AI when it writes something weird.
    """
    
    company_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Target company name"
    )
    company_website: HttpUrl = Field(
        ...,
        description="Company homepage URL"
    )
    target_role: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Job title of the recipient"
    )
    product_description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Description of the product/service being offered"
    )
    outreach_goal: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Desired outcome of the outreach"
    )
    tone: Literal["professional", "casual", "founder"] = Field(
        ...,
        description="Tone of the email"
    )

    @field_validator("company_name", "target_role", "product_description", "outreach_goal")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """
        Clean up those sneaky spaces.
        You'd be surprised how many people paste " Acme Corp " with spaces.
        """
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "company_name": "Acme Corp",
                    "company_website": "https://acme.com",
                    "target_role": "VP of Engineering",
                    "product_description": "AI-powered code review tool that reduces PR review time by 50%",
                    "outreach_goal": "Book a 15-minute demo call",
                    "tone": "professional"
                }
            ]
        }
    }


class OutreachOutput(BaseModel):
    """
    What you get back after the AI does its thing.
    
    If any of these fields are missing, something went very wrong
    and you should probably check the logs (or just run it again lol).
    """
    
    subject_lines: List[str] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Exactly 3 email subject lines - not 2, not 4, exactly 3"
    )
    primary_email: str = Field(
        ...,
        description="Primary cold email body (max 120 words)"
    )
    follow_up_email: str = Field(
        ...,
        description="Follow-up email body (max 120 words)"
    )
    personalization_points: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Personalization hooks extracted from research"
    )
    spam_risk_score: Literal["low", "medium", "high"] = Field(
        ...,
        description="Spam risk assessment"
    )

    @field_validator("subject_lines")
    @classmethod
    def validate_subject_lines_count(cls, v: List[str]) -> List[str]:
        """
        Why 3 subject lines? Because A/B testing is for winners.
        Also Masumi spec said 3, and we don't argue with specs.
        """
        if len(v) != 3:
            raise ValueError("Must provide exactly 3 subject lines - this isn't negotiable")
        return v


class ResearchOutput(BaseModel):
    """
    What the research agent digs up about a company.
    Think of it as corporate stalking, but legal and helpful.
    """
    
    industry: str = Field(..., description="Company industry/sector")
    value_proposition: str = Field(..., description="Company's main value proposition")
    personalization_hooks: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Personalization opportunities found"
    )
    company_summary: str = Field(..., description="Brief company summary")


class CopyOutput(BaseModel):
    """The good stuff - actual emails that (hopefully) don't suck."""
    
    subject_lines: List[str] = Field(..., min_length=3, max_length=3)
    primary_email: str  # the main pitch
    follow_up_email: str  # for when they ghost you the first time


class QAOutput(BaseModel):
    """
    The spam police verdict.
    
    Nobody wants their carefully crafted email to land in the 
    promotional tab of doom. This helps prevent that tragedy.
    """
    
    spam_risk_score: Literal["low", "medium", "high"]
    risk_factors: List[str] = Field(default_factory=list)  # what triggered the alarm
    analysis_notes: str = Field(default="")  # extra context if needed


class HealthResponse(BaseModel):
    """Proof that we're still alive. Not much else to say here."""
    status: str = "ok"


class ErrorResponse(BaseModel):
    """
    When things go wrong (and they will), this is what you get.
    At least we're honest about our failures.
    """
    error: str
    message: str
    details: List[str] = Field(default_factory=list)
