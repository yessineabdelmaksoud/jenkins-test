from fastapi import FastAPI, Request, BackgroundTasks
import logging
import os
from dotenv import load_dotenv

# load .env if present
load_dotenv()

from ai_agents.agents.registry import get_agent
from ai_agents.execution.runner import run_agent

app = FastAPI()
logger = logging.getLogger("jenkins_agent_server")
logging.basicConfig(level=logging.INFO)


def process_webhook(payload: dict) -> None:
    """Background task: instantiate agent and run workflow with the webhook payload."""
    try:
        # Only process completed builds to avoid duplicate processing
        build_info = payload.get("build", {})
        phase = build_info.get("phase", "").upper()
        status = build_info.get("status", "").upper()
        
        # Process COMPLETED builds with final status (logs should be available)
        # Skip FINALIZED as it might be too early for log availability
        if phase != "COMPLETED" or not status:
            logger.info("Skipping webhook - phase: %s, status: %s", phase, status)
            return
            
        logger.info("Processing webhook payload: %s", {k: payload.get(k) for k in list(payload.keys())[:5]} if isinstance(payload, dict) else str(payload))
        agent = get_agent("jenkins_agent")
        # Pass payload as 'input' so handlers can use state.get('input')
        result = run_agent(agent, {"input": payload})
        logger.info("Agent run completed. Result keys: %s", list(result.keys()) if isinstance(result, dict) else type(result))
    except Exception:
        logger.exception("Error processing webhook payload")


@app.post("/webhook")
async def webhook_endpoint(request: Request, background_tasks: BackgroundTasks):
    """Receives a JSON webhook and starts the JenkinsAgent in background.

    Returns immediately with 202 Accepted.
    """
    payload = await request.json()
    background_tasks.add_task(process_webhook, payload)
    return {"status": "accepted"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    # When running directly, ensure PYTHONPATH includes src if needed
    uvicorn.run("ai_agents.agents.jenkins_agent.server:app", host=host, port=port, log_level="info")
