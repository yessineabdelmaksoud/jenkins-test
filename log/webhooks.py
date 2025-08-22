"""Webhook endpoints for AI Agents API."""

from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from typing import Dict, Any
import logging
import json

from ai_agents.agents.registry import get_agent
from ai_agents.execution.runner import run_agent

router = APIRouter()
logger = logging.getLogger("webhooks")


def process_jenkins_webhook(payload: Dict[str, Any]) -> None:
    """Background task: process Jenkins webhook with JenkinsAgent."""
    try:
        # Only process completed builds to avoid duplicate processing
        build_info = payload.get("build", {})
        phase = build_info.get("phase", "").upper()
        status = build_info.get("status", "").upper()
        
        # Process COMPLETED builds with final status (logs should be available)
        if phase != "COMPLETED" or not status:
            logger.info("Skipping webhook - phase: %s, status: %s", phase, status)
            return
            
        logger.info("Processing Jenkins webhook payload for job: %s, build: %s, status: %s", 
                   payload.get("job_name", payload.get("name", "unknown")),
                   build_info.get("number", "unknown"),
                   status)
        
        # Get Jenkins agent and run it
        agent = get_agent("jenkins_agent")
        result = run_agent(agent, {"input": payload})
        
        logger.info("Jenkins agent processing completed. Result keys: %s", 
                   list(result.keys()) if isinstance(result, dict) else type(result))
        
    except Exception as e:
        logger.exception("Error processing Jenkins webhook payload: %s", str(e))


@router.post("/webhook")
async def jenkins_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Jenkins webhook endpoint.
    
    Receives Jenkins build notifications and processes them with the Jenkins Agent.
    Returns immediately with 202 Accepted while processing happens in background.
    
    Expected payload format:
    ```json
    {
        "name": "job-name",
        "job_name": "job-name", 
        "build": {
            "number": 123,
            "status": "SUCCESS|FAILURE|UNSTABLE|ABORTED",
            "phase": "COMPLETED|FINALIZED",
            "url": "http://jenkins/job/job-name/123/"
        },
        "jenkins_url": "http://jenkins-server",
        "jenkins_user": "username",
        "jenkins_token": "api-token"
    }
    ```
    """
    try:
        payload = await request.json()
        logger.info("Received Jenkins webhook: %s", 
                   {k: payload.get(k) for k in ['name', 'job_name'] if k in payload})
        
        # Add webhook processing to background tasks
        background_tasks.add_task(process_jenkins_webhook, payload)
        
        return {
            "status": "accepted",
            "message": "Jenkins webhook received and queued for processing"
        }
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.exception("Error processing webhook: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/webhook/health")
async def webhook_health():
    """Health check for webhook endpoint."""
    return {
        "status": "healthy",
        "endpoint": "/webhook",
        "description": "Jenkins webhook endpoint for build notifications"
    }


@router.post("/webhook/test")
async def test_webhook(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Test endpoint for webhook functionality.
    
    Allows testing the Jenkins webhook processing without requiring
    actual Jenkins server integration.
    """
    logger.info("Test webhook received: %s", payload)
    
    # Add test payload processing to background tasks
    background_tasks.add_task(process_jenkins_webhook, payload)
    
    return {
        "status": "accepted",
        "message": "Test webhook received and queued for processing",
        "payload_summary": {
            "job_name": payload.get("job_name", payload.get("name")),
            "build_number": payload.get("build", {}).get("number"),
            "status": payload.get("build", {}).get("status")
        }
    }
