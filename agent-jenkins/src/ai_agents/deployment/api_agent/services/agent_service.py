"""Agent service for managing agent operations."""

import asyncio
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import traceback 

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from ai_agents.agents.registry import AGENT_REGISTRY, get_agent
from ai_agents.deployment.api_agent.api.models.agent import (
    AgentInfo,
    AgentDetailedInfo,
    AgentConfig,
    AgentRunResponse, 
    AgentStatusResponse,
    AgentStatus,
    AgentType
)
from ai_agents.deployment.api_agent.core.logging import get_logger
from ai_agents.deployment.api_agent.core.config import get_settings

logger = get_logger(__name__)


class AgentService:
    """Service for managing AI agents."""
    
    def __init__(self):
        """Initialize the agent service."""
        self.settings = get_settings()
        self.running_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_runs: Dict[str, Dict[str, AgentRunResponse]] = {}
        
    async def list_agents(self) -> List[AgentInfo]:
        """
        Liste tous les agents disponibles.
        
        Returns:
            List[AgentInfo]: Liste des agents disponibles
        """
        agents = []
        
        for agent_id, agent_class in AGENT_REGISTRY.items():
            try:
                # Obtenir les informations de base de l'agent
                agent_info = AgentInfo(
                    id=agent_id,
                    name=agent_id.replace("_", " ").title(),
                    type=self._get_agent_type(agent_id),
                    description=f"Agent {agent_id} for specialized tasks",
                    version="1.0.0",
                    status=self._get_agent_status(agent_id)
                )
                agents.append(agent_info)
                
            except Exception as e:
                logger.warning(f"Could not load agent {agent_id}: {str(e)}")
                continue
                
        return agents
    
    async def get_agent_details(self, agent_id: str) -> Optional[AgentDetailedInfo]:
        """
        Obtient les détails d'un agent spécifique.
        
        Args:
            agent_id: Identifiant de l'agent
            
        Returns:
            Optional[AgentDetailedInfo]: Détails de l'agent ou None si non trouvé
        """
        if agent_id not in AGENT_REGISTRY:
            return None
            
        try:
            agent_class = AGENT_REGISTRY[agent_id]
            config_dict = agent_class.load_config()
            
            agent_config = AgentConfig(
                workflow=config_dict.get("workflow", {}),
                state_schema=config_dict.get("state_schema"),
                memory=config_dict.get("memory"),
                model=config_dict.get("model")
            )
            
            return AgentDetailedInfo(
                id=agent_id,
                name=agent_id.replace("_", " ").title(),
                type=self._get_agent_type(agent_id),
                description=f"Agent {agent_id} for specialized tasks",
                version="1.0.0",
                status=self._get_agent_status(agent_id),
                config=agent_config,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting agent details for {agent_id}: {str(e)}")
            return None
    
    async def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """
        Obtient la configuration d'un agent.
        
        Args:
            agent_id: Identifiant de l'agent
            
        Returns:
            Optional[AgentConfig]: Configuration de l'agent ou None si non trouvé
        """
        if agent_id not in AGENT_REGISTRY:
            return None
            
        try:
            agent_class = AGENT_REGISTRY[agent_id]
            config_dict = agent_class.load_config()
            
            return AgentConfig(
                workflow=config_dict.get("workflow", {}),
                state_schema=config_dict.get("state_schema"),
                memory=config_dict.get("memory"),
                model=config_dict.get("model")
            )
            
        except Exception as e:
            logger.error(f"Error getting agent config for {agent_id}: {str(e)}")
            return None
    
    async def agent_exists(self, agent_id: str) -> bool:
        """
        Vérifie si un agent existe.
        
        Args:
            agent_id: Identifiant de l'agent
            
        Returns:
            bool: True si l'agent existe
        """
        return agent_id in AGENT_REGISTRY
    
    async def execute_agent(
        self,
        agent_id: str,
        run_id: str,
        input_data: Dict[str, Any],
        config_override: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> None:
        """
        Exécute un agent de manière asynchrone.
        
        Args:
            agent_id: Identifiant de l'agent
            run_id: Identifiant de l'exécution
            input_data: Données d'entrée
            config_override: Surcharge de configuration
            timeout: Timeout d'exécution
        """
        # Initialiser l'enregistrement de l'exécution
        if agent_id not in self.agent_runs:
            self.agent_runs[agent_id] = {}
            
        run_response = AgentRunResponse(
            run_id=run_id,
            agent_id=agent_id,
            status=AgentStatus.RUNNING,
            started_at=datetime.now(),
            logs=[]
        )
        
        self.agent_runs[agent_id][run_id] = run_response
        
        try:
            # Marquer l'agent comme en cours d'exécution
            self.running_agents[agent_id] = {
                "run_id": run_id,
                "started_at": datetime.now(),
                "status": AgentStatus.RUNNING
            }
            
            # Charger et exécuter l'agent
            agent = get_agent(agent_id)
            
            # Appliquer les surcharges de configuration si fournies
            if config_override:
                # Ici, vous pourriez implémenter la logique pour appliquer les surcharges
                logger.info(f"Config override provided for {agent_id}: {config_override}")
            
            # Exécuter l'agent
            logger.info(f"Starting execution of agent {agent_id} with run_id {run_id}")
            run_response.logs.append(f"Starting execution at {datetime.now()}")
            
            # Exécution avec timeout
            timeout_seconds = timeout or self.settings.MAX_EXECUTION_TIME
            
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(agent.run, input_data),
                    timeout=timeout_seconds
                )
                
                # Succès
                run_response.status = AgentStatus.COMPLETED
                run_response.completed_at = datetime.now()
                run_response.result = result
                run_response.logs.append(f"Execution completed successfully at {datetime.now()}")
                
                
            except asyncio.TimeoutError:
                # Timeout
                run_response.status = AgentStatus.FAILED
                run_response.completed_at = datetime.now()
                run_response.error = f"Execution timed out after {timeout_seconds} seconds"
                run_response.logs.append(f"Execution timed out at {datetime.now()}")
                
                logger.warning(f"Agent {agent_id} execution timed out")
                
        except Exception as e:
            # Erreur d'exécution
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            run_response.status = AgentStatus.FAILED
            run_response.completed_at = datetime.now()
            run_response.error = error_msg
            run_response.logs.append(f"Execution failed at {datetime.now()}: {error_msg}")
            
            logger.error(f"Agent {agent_id} execution failed: {error_msg}")
            logger.debug(f"Full traceback: {error_trace}")
            
        finally:
            # Mettre à jour l'enregistrement final AVANT de nettoyer
            self.agent_runs[agent_id][run_id] = run_response

            # Nettoyer l'état d'exécution
            if agent_id in self.running_agents:
                del self.running_agents[agent_id]

            logger.info(f"Agent {agent_id} execution finished. Final status: {run_response.status}")
    
    async def get_agent_status(
        self,
        agent_id: str,
        run_id: Optional[str] = None
    ) -> AgentStatusResponse:
        """
        Obtient le statut d'un agent.

        Args:
            agent_id: Identifiant de l'agent
            run_id: Identifiant de l'exécution (optionnel)

        Returns:
            AgentStatusResponse: Statut de l'agent
        """
        # Statut actuel de l'agent
        current_status = AgentStatus.IDLE
        last_activity = None
        current_run = None
        actual_run_id = run_id

        # Vérifier si l'agent est en cours d'exécution
        if agent_id in self.running_agents:
            current_status = self.running_agents[agent_id]["status"]
            last_activity = self.running_agents[agent_id]["started_at"]
            actual_run_id = run_id or self.running_agents[agent_id]["run_id"]

        # Obtenir les détails de l'exécution si spécifiée
        if actual_run_id and agent_id in self.agent_runs and actual_run_id in self.agent_runs[agent_id]:
            current_run = self.agent_runs[agent_id][actual_run_id]
            if not last_activity:
                last_activity = current_run.started_at
            # Utiliser le statut de l'exécution si elle est terminée
            if current_run.status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.CANCELLED]:
                current_status = current_run.status
        elif agent_id in self.agent_runs and self.agent_runs[agent_id]:
            # Prendre la dernière exécution
            latest_run_id = max(self.agent_runs[agent_id].keys(),
                              key=lambda x: self.agent_runs[agent_id][x].started_at)
            current_run = self.agent_runs[agent_id][latest_run_id]
            actual_run_id = latest_run_id
            if not last_activity:
                last_activity = current_run.started_at
            # Utiliser le statut de l'exécution si elle est terminée
            if current_run.status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.CANCELLED]:
                current_status = current_run.status

        return AgentStatusResponse(
            agent_id=agent_id,
            run_id=actual_run_id,
            status=current_status,
            last_activity=last_activity,
            current_run=current_run
        )
     
    async def get_run_details(
        self,
        agent_id: str,
        run_id: str
    ) -> Optional[AgentRunResponse]:
        """
        Obtient les détails d'une exécution spécifique.

        Args:
            agent_id: Identifiant de l'agent
            run_id: Identifiant de l'exécution

        Returns:
            Optional[AgentRunResponse]: Détails de l'exécution ou None si non trouvé
        """
        logger.debug(f"Looking for run {run_id} for agent {agent_id}")
        logger.debug(f"Available agents in runs: {list(self.agent_runs.keys())}")

        if agent_id in self.agent_runs:
            logger.debug(f"Available runs for {agent_id}: {list(self.agent_runs[agent_id].keys())}")
            if run_id in self.agent_runs[agent_id]:
                run_details = self.agent_runs[agent_id][run_id]
                logger.debug(f"Found run {run_id}: status={run_details.status}")
                return run_details

        logger.warning(f"Run {run_id} not found for agent {agent_id}")
        return None

    async def list_agent_runs(self, agent_id: str) -> List[AgentRunResponse]:
        """
        Liste toutes les exécutions d'un agent.

        Args:
            agent_id: Identifiant de l'agent

        Returns:
            List[AgentRunResponse]: Liste des exécutions
        """
        if agent_id in self.agent_runs:
            runs = list(self.agent_runs[agent_id].values())
            # Trier par date de début (plus récent en premier)
            runs.sort(key=lambda x: x.started_at, reverse=True)
            return runs
        return []
    
    async def cancel_run(self, agent_id: str, run_id: str) -> bool:
        """
        Annule une exécution en cours.
        
        Args:
            agent_id: Identifiant de l'agent
            run_id: Identifiant de l'exécution
            
        Returns:
            bool: True si l'annulation a réussi
        """
        # Vérifier si l'exécution existe et est en cours
        if (agent_id in self.running_agents and 
            self.running_agents[agent_id]["run_id"] == run_id):
            
            # Marquer comme annulé
            if agent_id in self.agent_runs and run_id in self.agent_runs[agent_id]:
                run_response = self.agent_runs[agent_id][run_id]
                run_response.status = AgentStatus.CANCELLED
                run_response.completed_at = datetime.now()
                run_response.logs.append(f"Execution cancelled at {datetime.now()}")
            
            # Nettoyer l'état d'exécution
            del self.running_agents[agent_id]
            
            logger.info(f"Cancelled run {run_id} for agent {agent_id}")
            return True
            
        return False

    def _get_agent_type(self, agent_id: str) -> AgentType:
        """Obtient le type d'agent basé sur son ID."""
        if agent_id == "sales_assistant":
            return AgentType.SALES_ASSISTANT
        elif agent_id == "calculator":
            return AgentType.CALCULATOR
        elif agent_id == "jenkins":
            return AgentType.JENKINS_AGENT
        else:
            return AgentType.CALCULATOR  # Default to calculator (no OpenAI required)
    
    def _get_agent_status(self, agent_id: str) -> AgentStatus:
        """Obtient le statut actuel d'un agent."""
        if agent_id in self.running_agents:
            return self.running_agents[agent_id]["status"]
        return AgentStatus.IDLE
    
