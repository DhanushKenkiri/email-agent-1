"""
API Routes - Where HTTP meets AI.

Two endpoints, that's it:
- POST /run  → Do the thing
- GET /health → Are we alive?

Simple is good. Simple doesn't break at 3am.
"""

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from .schemas import OutreachInput, OutreachOutput, HealthResponse, ErrorResponse
from .crew import OutreachCrew
from .utils.web_scraper import ScraperError

router = APIRouter()


@router.post(
    "/run",
    response_model=OutreachOutput,
    responses={
        400: {"model": ErrorResponse, "description": "You sent us garbage"},
        502: {"model": ErrorResponse, "description": "Website is hiding from us"},
        500: {"model": ErrorResponse, "description": "We messed up somehow"},
    }
)
def run_outreach_agent(input_data: OutreachInput) -> OutreachOutput:
    """
    Generate cold outreach emails for a target company.
    
    Send us company info, get back personalized emails.
    It's like having a sales copywriter on demand, except
    this one doesn't need coffee breaks.
    
    Warning: This can take 15-30 seconds. The AI is thinking.
    Don't spam refresh.
    """
    try:
        crew = OutreachCrew()
        result = crew.run(input_data)
        return result
    
    except ScraperError as e:
        # website was unreachable, blocked us, or just doesn't exist
        raise HTTPException(
            status_code=502,
            detail={
                "error": "scrape_failed",
                "message": str(e),
                "details": ["Maybe check if the URL is correct?"]
            }
        )
    
    except ValidationError as e:
        # agent returned something weird that doesn't match our schema
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_error",
                "message": "Agent output validation failed - this is embarrassing",
                "details": [str(err) for err in e.errors()]
            }
        )
    
    except ValueError as e:
        # usually means JSON parsing failed
        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_error",
                "message": str(e),
                "details": ["The AI might be having a bad day. Try again?"]
            }
        )
    
    except Exception as e:
        # something truly unexpected - log this one
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Unexpected error: {str(e)}",
                "details": ["If this keeps happening, we have a bug."]
            }
        )


@router.get(
    "/health",
    response_model=HealthResponse
)
def health_check() -> HealthResponse:
    """
    Check if the service is alive.
    
    Returns "ok" if we're running. Doesn't mean everything works,
    just that we're not dead. Low bar, but an important one.
    """
    return HealthResponse(status="ok")
