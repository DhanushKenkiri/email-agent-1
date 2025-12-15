"""
Cold Outreach Email Agent - Main Entry Point

This is where FastAPI wakes up and starts accepting requests.
Nothing fancy here, just wiring things together and hoping
for the best. (Just kidding, we tested this. Mostly.)

To run locally:
    uvicorn app.main:app --reload

To run in prod:
    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

import os
from dotenv import load_dotenv

# Load .env file before anything else touches env vars
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router

# create the app with some nice metadata for the docs
app = FastAPI(
    title="Cold Outreach Email Agent",
    description="AI-powered cold email generation. No spam, just personalized emails that might actually get read.",
    version="1.0.0",
    docs_url="/docs",  # swagger ui lives here
    redoc_url="/redoc"  # for the fancy docs enjoyers
)

# CORS - allowing everything because Masumi might call from anywhere
# (yes security people, we know, but this is an internal API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# plug in our routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """
    Runs when the server starts.
    Just a friendly log message so we know things are working.
    """
    print("🚀 Cold Outreach Agent is alive and ready to write emails")
    print("📖 Docs available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the server stops.
    Goodbye cruel world, etc.
    """
    print("👋 Cold Outreach Agent shutting down. Thanks for the memories.")
