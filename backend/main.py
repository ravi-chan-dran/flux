"""
FLUX - Orbital Research Agent
FastAPI Backend Main Application
"""

import os
import uuid
import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from loguru import logger
import sys

from flux_core.graph.research_graph import stream_research
from flux_core.graph.state import create_initial_state
from flux_core.tools.storage import (
    ensure_storage_dirs,
    save_paper,
    load_paper,
    list_papers,
    get_storage_info,
)

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.remove()
logger.add(
    sys.stderr,
    level=log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting FLUX Research Agent backend...")
    logger.info(f"Log level: {log_level}")
    logger.info(f"AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    logger.info(f"Max Iterations: {os.getenv('MAX_ITERATIONS', '1')}")
    logger.info(f"Quality Threshold: {os.getenv('QUALITY_THRESHOLD', '8.0')}")
    
    # Create storage directories
    logger.info("Ensuring storage directories exist...")
    ensure_storage_dirs()
    storage_info = get_storage_info()
    logger.info(f"Storage: {storage_info['paper_count']} papers, {storage_info['total_size_mb']}MB")
    
    yield
    
    logger.info("Shutting down FLUX Research Agent backend...")


# Initialize FastAPI application
app = FastAPI(
    title="FLUX Research Agent",
    description="Orbital research system powered by LangGraph and AWS Bedrock",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "service": "FLUX Research Agent",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "flux-backend",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/config")
async def get_config() -> dict[str, Any]:
    """Get current configuration (non-sensitive values)."""
    return {
        "max_iterations": int(os.getenv("MAX_ITERATIONS", "1")),
        "quality_threshold": float(os.getenv("QUALITY_THRESHOLD", "8.0")),
        "improvement_threshold": float(os.getenv("IMPROVEMENT_THRESHOLD", "0.5")),
        "log_level": log_level,
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "model_id": os.getenv("AWS_BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"),
    }


# Pydantic models

class ResearchRequest(BaseModel):
    """Request model for starting research."""
    question: str = Field(..., min_length=10, description="Research question to investigate")
    max_iterations: int | None = Field(None, ge=1, le=10, description="Max orbital iterations")
    quality_threshold: float | None = Field(None, ge=0.0, le=10.0, description="Quality threshold")
    improvement_threshold: float | None = Field(None, ge=0.0, le=5.0, description="Improvement threshold")


class ResearchResponse(BaseModel):
    """Response model for research start."""
    research_id: str
    question: str
    status: str
    message: str


# Research endpoints

@app.post("/api/research/start", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
) -> ResearchResponse:
    """
    Start a new research task.
    
    Creates a research ID and begins background processing through the orbital workflow.
    
    Args:
        request: Research request with question and optional parameters
        background_tasks: FastAPI background tasks manager
    
    Returns:
        ResearchResponse with research_id and status
    """
    # Generate unique research ID
    research_id = f"research-{uuid.uuid4().hex[:12]}"
    
    logger.info(f"Starting research: {research_id}")
    logger.info(f"Question: {request.question}")
    
    # Prepare configuration
    config = {}
    if request.max_iterations:
        config["max_iterations"] = request.max_iterations
    if request.quality_threshold:
        config["quality_threshold"] = request.quality_threshold
    if request.improvement_threshold:
        config["improvement_threshold"] = request.improvement_threshold
    
    # Note: Background task execution would go here
    # For now, we'll use the streaming endpoint instead
    
    return ResearchResponse(
        research_id=research_id,
        question=request.question,
        status="initiated",
        message=f"Research initiated. Use /api/research/{research_id}/stream to follow progress.",
    )


@app.get("/api/research/{research_id}/stream")
async def stream_research_progress(research_id: str, question: str):
    """
    Stream research progress via Server-Sent Events (SSE).
    
    Runs the orbital research workflow and yields state updates as they occur.
    
    Args:
        research_id: Unique research identifier
        question: Research question (passed as query parameter)
    
    Returns:
        EventSourceResponse with SSE events
    """
    logger.info(f"🌊 Starting SSE stream for research: {research_id}")
    logger.info(f"📝 Question: {question}")
    
    async def event_generator():
        """Generate SSE events from research workflow."""
        last_ping = asyncio.get_event_loop().time()
        
        try:
            # Send connection established event
            yield {
                "event": "connected",
                "data": json.dumps({
                    "research_id": research_id,
                    "status": "connected",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            }
            
            # Configuration from environment
            config = {
                "max_iterations": int(os.getenv("MAX_ITERATIONS", "1")),
                "quality_threshold": float(os.getenv("QUALITY_THRESHOLD", "8.0")),
                "improvement_threshold": float(os.getenv("IMPROVEMENT_THRESHOLD", "0.5")),
            }
            
            # Stream research updates
            async for event in stream_research(question, research_id, **config):
                # Send the event
                yield {
                    "event": event.get("event_type", "message"),
                    "data": json.dumps({
                        **event,
                        "research_id": research_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                }
                
                last_ping = asyncio.get_event_loop().time()
                
                # Small delay for better streaming experience
                await asyncio.sleep(0.05)
                
                # Send ping every 30 seconds to keep connection alive
                current_time = asyncio.get_event_loop().time()
                if current_time - last_ping > 30:
                    yield {
                        "event": "ping",
                        "data": json.dumps({"timestamp": datetime.utcnow().isoformat()})
                    }
                    last_ping = current_time
            
            # Final completion event
            yield {
                "event": "complete",
                "data": json.dumps({
                    "research_id": research_id,
                    "status": "complete",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            }
            
            logger.info(f"✅ Research stream completed: {research_id}")
            
        except Exception as e:
            logger.error(f"❌ Error streaming research {research_id}: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps({
                    "research_id": research_id,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                })
            }
    
    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@app.get("/api/research/{research_id}/paper")
async def get_paper(research_id: str):
    """
    Get completed research paper.
    
    Args:
        research_id: Unique research identifier
    
    Returns:
        Paper content and metadata
    
    Raises:
        HTTPException: If paper not found
    """
    logger.info(f"Fetching paper: {research_id}")
    
    try:
        paper_data = await load_paper(research_id)
        
        return {
            "research_id": research_id,
            "paper": paper_data["paper"],
            "metadata": paper_data["metadata"],
            "status": "completed",
        }
    
    except Exception as e:
        logger.error(f"Failed to load paper {research_id}: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Paper not found: {research_id}"
        )


@app.get("/api/research/list")
async def list_research():
    """
    List all completed research papers.
    
    Returns:
        List of paper metadata sorted by date
    """
    logger.info("Listing all research papers")
    
    try:
        papers = await list_papers()
        
        return {
            "papers": papers,
            "count": len(papers),
            "storage_info": get_storage_info(),
        }
    
    except Exception as e:
        logger.error(f"Failed to list papers: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve paper list"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "type": type(exc).__name__,
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level=log_level.lower(),
    )

