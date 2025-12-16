"""
API Routes - Where HTTP meets AI.

MIP-003 Compliant Endpoints:
- POST /start_job      → Start a job
- GET  /status         → Check job status
- GET  /availability   → Health check (MIP-003 style)
- GET  /input_schema   → Get expected input format

Legacy Endpoints (still work):
- POST /run            → Do the thing
- GET  /health         → Are we alive?

Simple is good. Simple doesn't break at 3am.
"""

import hashlib
import json
import time
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from .schemas import (
    OutreachInput, OutreachOutput, HealthResponse, ErrorResponse,
    AvailabilityResponse, InputSchemaResponse, InputFieldSchema,
    StartJobRequest, StartJobResponse, JobStatusResponse
)
from .crew import OutreachCrew
from .utils.web_scraper import ScraperError

router = APIRouter()

# In-memory job storage (in production, use Redis or a database)
# This is fine for Sokosumi testing - jobs don't need to persist
jobs_store = {}


# =============================================
# MIP-003 COMPLIANT ENDPOINTS
# These are what Sokosumi expects
# =============================================

@router.get("/availability", response_model=AvailabilityResponse)
def check_availability() -> AvailabilityResponse:
    """
    MIP-003: Check if the agentic service is available.
    
    Sokosumi uses this to show the agent as "online" or "offline".
    """
    return AvailabilityResponse(
        status="available",
        type="masumi-agent",
        message="Cold Outreach Email Agent is ready to accept jobs"
    )


@router.get("/input_schema", response_model=InputSchemaResponse)
def get_input_schema() -> InputSchemaResponse:
    """
    MIP-003: Returns the expected input schema for /start_job.
    
    This tells Sokosumi what form fields to show the user.
    """
    return InputSchemaResponse(
        input_data=[
            InputFieldSchema(
                id="company_name",
                type="string",
                name="Company Name",
                data={"placeholder": "e.g., Stripe"},
                validations=[{"type": "required"}, {"type": "min_length", "value": 1}]
            ),
            InputFieldSchema(
                id="company_website",
                type="string",
                name="Company Website",
                data={"placeholder": "https://stripe.com"},
                validations=[{"type": "required"}, {"type": "url"}]
            ),
            InputFieldSchema(
                id="target_role",
                type="string",
                name="Target Role",
                data={"placeholder": "e.g., Head of Growth"},
                validations=[{"type": "required"}]
            ),
            InputFieldSchema(
                id="product_description",
                type="string",
                name="Your Product Description",
                data={"placeholder": "AI-powered tool that..."},
                validations=[{"type": "required"}, {"type": "min_length", "value": 10}]
            ),
            InputFieldSchema(
                id="outreach_goal",
                type="string",
                name="Outreach Goal",
                data={"placeholder": "Book a 15-minute demo call"},
                validations=[{"type": "required"}]
            ),
            InputFieldSchema(
                id="tone",
                type="option",
                name="Email Tone",
                data={
                    "options": [
                        {"value": "professional", "label": "Professional"},
                        {"value": "casual", "label": "Casual"},
                        {"value": "founder", "label": "Founder-to-Founder"}
                    ]
                },
                validations=[{"type": "required"}]
            )
        ]
    )


@router.post("/start_job", response_model=StartJobResponse)
def start_job(request: StartJobRequest) -> StartJobResponse:
    """
    MIP-003: Start a new job.
    
    This is the main entry point for Sokosumi to trigger jobs.
    The job runs synchronously for simplicity.
    """
    job_id = str(uuid.uuid4())
    status_id = str(uuid.uuid4())
    blockchain_id = f"block_{uuid.uuid4().hex[:12]}"
    
    # Calculate input hash for integrity
    input_json = json.dumps(request.input_data.model_dump(), sort_keys=True)
    input_hash = hashlib.sha256(input_json.encode()).hexdigest()
    
    # Timestamps (MIP-003 requires these)
    current_time = int(time.time())
    pay_by_time = current_time + 3600  # 1 hour to pay
    submit_result_time = current_time + 7200  # 2 hours to submit
    unlock_time = current_time + 10800  # 3 hours to unlock
    dispute_time = current_time + 86400  # 24 hours for disputes
    
    # Store initial job state
    jobs_store[job_id] = {
        "id": status_id,
        "job_id": job_id,
        "status": "running",
        "input_data": request.input_data,
        "identifier_from_purchaser": request.identifier_from_purchaser,
        "result": None
    }
    
    # Run the job synchronously (Sokosumi expects this for simple agents)
    try:
        crew = OutreachCrew()
        result = crew.run(request.input_data)
        
        jobs_store[job_id]["status"] = "completed"
        jobs_store[job_id]["result"] = result.model_dump_json()
        
    except Exception as e:
        jobs_store[job_id]["status"] = "failed"
        jobs_store[job_id]["result"] = json.dumps({"error": str(e)})
    
    return StartJobResponse(
        id=status_id,
        status="success",
        job_id=job_id,
        blockchainIdentifier=blockchain_id,
        payByTime=pay_by_time,
        submitResultTime=submit_result_time,
        unlockTime=unlock_time,
        externalDisputeUnlockTime=dispute_time,
        agentIdentifier="cold-outreach-email-agent-v1",
        sellerVKey="addr_placeholder",  # Will be set by Masumi Payment Service
        identifierFromPurchaser=request.identifier_from_purchaser,
        input_hash=input_hash
    )


@router.get("/status", response_model=JobStatusResponse)
def get_job_status(job_id: str = Query(..., description="The job ID to check")) -> JobStatusResponse:
    """
    MIP-003: Get the status of a job.
    
    Sokosumi polls this to know when a job is done.
    """
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail={"error": "Job not found"})
    
    job = jobs_store[job_id]
    return JobStatusResponse(
        id=job["id"],
        job_id=job["job_id"],
        status=job["status"],
        result=job["result"]
    )


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
