"""Agent management API routes."""

import os
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse
import uuid 
from datetime import datetime

from ai_agents.deployment.api_agent.api.models.agent import (
    AgentInfo,
    AgentDetailedInfo,
    AgentConfig,
    AgentRunRequest,
    AgentRunResponse,
    AgentStatusResponse,
    AgentListResponse,
    AgentStatus,
    AgentType,
    ErrorResponse
)
from ai_agents.deployment.api_agent.services.agent_service import AgentService
from ai_agents.deployment.api_agent.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Global agent service instance (singleton)
_agent_service = None

# Dependency to get agent service
def get_agent_service() -> AgentService:
    """Get agent service instance (singleton)."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service


@router.get("/agents", response_model=AgentListResponse)
async def list_agents(
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentListResponse:
    """
    Liste tous les agents disponibles.
    
    Returns:
        AgentListResponse: Liste des agents avec leurs informations de base
    """
    try:
        agents = await agent_service.list_agents()
        return AgentListResponse(
            agents=agents,
            total=len(agents)
        )
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/agents/{agent_id}", response_model=AgentDetailedInfo)
async def get_agent_details(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentDetailedInfo:
    """
    Obtient les informations détaillées d'un agent spécifique.
    
    Args:
        agent_id: Identifiant de l'agent
        
    Returns:
        AgentDetailedInfo: Informations détaillées de l'agent
    """
    try:
        agent_details = await agent_service.get_agent_details(agent_id)
        if not agent_details:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        return agent_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent details for {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent details: {str(e)}")


@router.get("/agents/{agent_id}/config", response_model=AgentConfig)
async def get_agent_config(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentConfig:
    """
    Lit la configuration actuelle d'un agent.
    
    Args:
        agent_id: Identifiant de l'agent
        
    Returns:
        AgentConfig: Configuration de l'agent
    """
    try:
        config = await agent_service.get_agent_config(agent_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent config for {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent config: {str(e)}")


@router.post("/agents/{agent_id}/run", response_model=AgentRunResponse)
async def run_agent(
    agent_id: str,
    request: AgentRunRequest,
    background_tasks: BackgroundTasks,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentRunResponse:
    """
    Lance l'exécution d'un agent avec les données fournies.
    
    Args:
        agent_id: Identifiant de l'agent
        request: Données d'entrée et configuration pour l'exécution
        background_tasks: Tâches en arrière-plan FastAPI
        
    Returns:
        AgentRunResponse: Informations sur l'exécution lancée
    """
    try:
        # Vérifier que l'agent existe
        agent_exists = await agent_service.agent_exists(agent_id)
        if not agent_exists:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        # Générer un ID unique pour cette exécution
        run_id = str(uuid.uuid4())
        
        # Créer la réponse initiale
        run_response = AgentRunResponse(
            run_id=run_id,
            agent_id=agent_id,
            status=AgentStatus.RUNNING,
            started_at=datetime.now(),
            logs=[]
        )
        
        # Lancer l'exécution en arrière-plan
        background_tasks.add_task(
            agent_service.execute_agent,
            agent_id,
            run_id,
            request.input_data,
            request.config_override,
            request.timeout
        )
        
        logger.info(f"Started execution of agent {agent_id} with run_id {run_id}")
        return run_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to run agent: {str(e)}")


@router.get("/agents/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(
    agent_id: str,
    run_id: str = None,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentStatusResponse:
    """
    Obtient l'état ou le résultat d'une exécution d'agent.
    
    Args:
        agent_id: Identifiant de l'agent
        run_id: Identifiant de l'exécution (optionnel, prend la dernière si non spécifié)
        
    Returns:
        AgentStatusResponse: État de l'agent et détails de l'exécution
    """
    try:
        # Vérifier que l'agent existe
        agent_exists = await agent_service.agent_exists(agent_id)
        if not agent_exists:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        status = await agent_service.get_agent_status(agent_id, run_id)
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status for {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@router.get("/agents/{agent_id}/runs", response_model=List[AgentRunResponse])
async def list_agent_runs(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service)
) -> List[AgentRunResponse]:
    """
    Liste toutes les exécutions d'un agent.

    Args:
        agent_id: Identifiant de l'agent

    Returns:
        List[AgentRunResponse]: Liste des exécutions
    """
    try:
        # Vérifier que l'agent existe
        agent_exists = await agent_service.agent_exists(agent_id)
        if not agent_exists:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        runs = await agent_service.list_agent_runs(agent_id)
        return runs

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing runs for {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list runs: {str(e)}")


@router.get("/agents/{agent_id}/runs/{run_id}", response_model=AgentRunResponse)
async def get_run_details(
    agent_id: str,
    run_id: str,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentRunResponse:
    """
    Obtient les détails d'une exécution spécifique.

    Args:
        agent_id: Identifiant de l'agent
        run_id: Identifiant de l'exécution

    Returns:
        AgentRunResponse: Détails de l'exécution
    """
    try:
        run_details = await agent_service.get_run_details(agent_id, run_id)
        if not run_details:
            raise HTTPException(
                status_code=404,
                detail=f"Run '{run_id}' not found for agent '{agent_id}'"
            )
        return run_details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting run details for {agent_id}/{run_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get run details: {str(e)}")


@router.delete("/agents/{agent_id}/runs/{run_id}")
async def cancel_run(
    agent_id: str,
    run_id: str,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, str]:
    """
    Annule une exécution en cours.
    
    Args:
        agent_id: Identifiant de l'agent
        run_id: Identifiant de l'exécution
        
    Returns:
        Dict: Message de confirmation
    """
    try:
        success = await agent_service.cancel_run(agent_id, run_id)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Run '{run_id}' not found or cannot be cancelled"
            )
        
        return {"message": f"Run {run_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling run {agent_id}/{run_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel run: {str(e)}")


@router.post("/jenkins/webhook")
async def jenkins_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    agent_service: AgentService = Depends(get_agent_service)
) -> Dict[str, str]:
    """
    Jenkins webhook endpoint that automatically triggers the Jenkins agent.
    
    This endpoint receives webhook notifications from Jenkins builds and
    automatically runs the jenkins_agent to process the build information.
    
    Configure this URL in Jenkins: http://your-server:8000/api/jenkins/webhook
    
    Returns:
        Dict: Acceptance confirmation with run_id
    """
    try:
        # Get the webhook payload
        payload = await request.json()
        logger.info(f"Received Jenkins webhook: {payload}")
        
        # Validate that this looks like a Jenkins webhook
        if not payload or not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Invalid webhook payload")
        
        # Enhance payload with missing data (like the standalone server)
        enhanced_payload = payload.copy()
        
        # Add jenkins_url from environment if not present
        if "jenkins_url" not in enhanced_payload:
            jenkins_url = os.getenv("JENKINS_URL", "http://localhost:8080")
            enhanced_payload["jenkins_url"] = jenkins_url
        
        # Ensure job_name is present
        if "job_name" not in enhanced_payload and "name" in enhanced_payload:
            enhanced_payload["job_name"] = enhanced_payload["name"]
        
        # Ensure build_number is present
        build_info = enhanced_payload.get("build", {})
        if "build_number" not in enhanced_payload and "number" in build_info:
            enhanced_payload["build_number"] = build_info["number"]
        
        # Apply exact same logic as server.py - only process COMPLETED builds
        phase = build_info.get("phase", "").upper()
        status = build_info.get("status", "").upper()
        
        # Process COMPLETED builds with final status (logs should be available)
        # Skip FINALIZED as it might be too early for log availability (like in server.py)
        if phase != "COMPLETED" or not status:
            logger.info(f"Skipping webhook - phase: {phase}, status: {status}")
            return {
                "status": "skipped", 
                "message": f"Webhook skipped - phase: {phase}, status: {status}",
                "reason": "Only processing COMPLETED builds with final status"
            }
        
        logger.info(f"Processing webhook - phase: {phase}, status: {status}")
        
        # Prepare input data for jenkins_agent (exactly like standalone server)
        # The server.py passes payload as 'input' so handlers can use state.get('input')
        input_data = {"input": enhanced_payload}
        
        # Generate unique run ID
        run_id = str(uuid.uuid4())
        
        # Create initial run response and store it in agent service
        run_response = AgentRunResponse(
            run_id=run_id,
            agent_id="jenkins_agent",
            status=AgentStatus.RUNNING,
            started_at=datetime.now(),
            logs=["Jenkins webhook received, starting agent execution..."]
        )
        
        # Store the run response in agent service
        if "jenkins_agent" not in agent_service.agent_runs:
            agent_service.agent_runs["jenkins_agent"] = {}
        agent_service.agent_runs["jenkins_agent"][run_id] = run_response
        
        
        # Trigger jenkins_agent execution in background using execute_agent
        background_tasks.add_task(
            agent_service.execute_agent,
            "jenkins_agent",    # agent_id
            run_id,             # run_id
            input_data,         # input_data
            None,               # config_override
            300                 # timeout
        )
        
        logger.info(f"Jenkins webhook triggered agent execution with run_id: {run_id}")
        
        return {
            "status": "accepted",
            "message": "Jenkins webhook received and jenkins_agent triggered",
            "run_id": run_id,
            "agent_id": "jenkins_agent",
            "webhook_url": f"/api/agents/jenkins_agent/runs/{run_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Jenkins webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")


