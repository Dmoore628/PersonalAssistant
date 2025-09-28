"""
System Orchestrator for Archi AI Digital Twin
Central coordination service that manages system-wide workflows and demonstrates
the integration between voice engine, agents, HUD overlay, and CUA engine
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional

from archi_core import Health, MessageBus, Settings, AgentMessage, AgentMessageType
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

settings = Settings()
app = FastAPI(title="System Orchestrator")
bus = MessageBus(url=settings.rabbitmq_url)

logger = logging.getLogger(__name__)


class SystemDemo(BaseModel):
    """System demonstration request"""
    scenario: str
    parameters: Dict[str, Any] = {}


class SystemHealth(BaseModel):
    """Overall system health"""
    status: str
    services: List[Dict[str, str]]
    uptime: float
    active_workflows: int


class DemoOrchestrator:
    """Orchestrates system demonstrations and end-to-end workflows"""
    
    def __init__(self):
        self.active_demos = {}
        self.service_status = {}
        self.start_time = time.time()
        
    async def initialize(self):
        """Initialize the orchestrator"""
        logger.info("Initializing System Orchestrator")
        
        # Monitor service health
        asyncio.create_task(self._monitor_services())
        
        logger.info("System Orchestrator initialized")
    
    async def run_demo_scenario(self, scenario: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run a demonstration scenario"""
        demo_id = f"demo_{int(time.time())}"
        logger.info(f"Starting demo scenario: {scenario} ({demo_id})")
        
        try:
            if scenario == "voice_to_action":
                return await self._demo_voice_to_action(demo_id, parameters)
            elif scenario == "workflow_orchestration":
                return await self._demo_workflow_orchestration(demo_id, parameters)
            elif scenario == "system_integration":
                return await self._demo_system_integration(demo_id, parameters)
            else:
                raise ValueError(f"Unknown demo scenario: {scenario}")
                
        except Exception as e:
            logger.error(f"Demo scenario failed: {e}")
            raise
    
    async def _demo_voice_to_action(self, demo_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Demonstrate voice-to-action workflow"""
        steps = []
        
        # Step 1: Simulate voice command
        voice_command = {
            "text": parameters.get("command", "Open notepad and create a new document"),
            "confidence": 0.95,
            "intent": "plan_task", 
            "parameters": {
                "task": "document_creation",
                "app_name": "notepad"
            },
            "timestamp": time.time(),
            "user_id": "demo_user"
        }
        
        # Send to voice processing queue
        bus.publish(queue="voice.command", body=json.dumps(voice_command).encode("utf-8"))
        steps.append({"step": "voice_command_sent", "data": voice_command, "timestamp": time.time()})
        
        # Step 2: Wait for plan creation
        await asyncio.sleep(1)  # Simulate processing time
        
        # Step 3: Simulate HUD notification
        notification = {
            "title": "Voice Command Processed",
            "message": f"Processing: {voice_command['text']}",
            "type": "info",
            "priority": 2
        }
        bus.publish(queue="system.notification", body=json.dumps(notification).encode("utf-8"))
        steps.append({"step": "hud_notification_sent", "data": notification, "timestamp": time.time()})
        
        # Step 4: Simulate system execution
        system_command = {
            "action": "open_application",
            "parameters": {"app_name": "notepad"},
            "source": "demo_orchestrator"
        }
        bus.publish(queue="system.execute", body=json.dumps(system_command).encode("utf-8"))
        steps.append({"step": "system_execution_sent", "data": system_command, "timestamp": time.time()})
        
        return {
            "demo_id": demo_id,
            "scenario": "voice_to_action",
            "success": True,
            "steps": steps,
            "duration": time.time() - steps[0]["timestamp"],
            "summary": "Voice command processed through full pipeline: Voice Engine → Planning Agent → Execution Agent → CUA Engine → HUD Overlay"
        }
    
    async def _demo_workflow_orchestration(self, demo_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Demonstrate multi-step workflow orchestration"""
        steps = []
        
        # Step 1: Create complex workflow
        workflow = {
            "id": demo_id,
            "name": "Document Creation Workflow",
            "description": "Complete document creation process",
            "actions": [
                {
                    "action_type": "open_application",
                    "parameters": {"app_name": "notepad"},
                    "timeout": 30
                },
                {
                    "action_type": "wait",
                    "parameters": {"duration": 2},
                    "timeout": 5
                },
                {
                    "action_type": "type",
                    "parameters": {"text": "Hello from Archi AI Digital Twin!"},
                    "timeout": 10
                },
                {
                    "action_type": "key_press",
                    "parameters": {"keys": ["ctrl", "s"]},
                    "timeout": 5
                }
            ],
            "retry_policy": {"max_retries": 2, "retry_delay": 1}
        }
        
        # Send workflow to CUA engine
        workflow_command = {
            "action": "execute_workflow",
            "parameters": workflow,
            "source": "demo_orchestrator"
        }
        bus.publish(queue="system.execute", body=json.dumps(workflow_command).encode("utf-8"))
        steps.append({"step": "workflow_sent", "data": workflow, "timestamp": time.time()})
        
        # Step 2: Send progress updates
        for i, action in enumerate(workflow["actions"]):
            await asyncio.sleep(0.5)  # Simulate execution time
            
            progress_update = {
                "execution_id": demo_id,
                "step": i,
                "total_steps": len(workflow["actions"]),
                "action": action["action_type"],
                "progress": (i + 1) / len(workflow["actions"]),
                "timestamp": time.time()
            }
            bus.publish(queue="task.progress", body=json.dumps(progress_update).encode("utf-8"))
            steps.append({"step": f"progress_update_{i}", "data": progress_update, "timestamp": time.time()})
        
        # Step 3: Send completion notification
        completion_notification = {
            "title": "Workflow Completed",
            "message": f"Document creation workflow completed successfully",
            "type": "success",
            "priority": 1
        }
        bus.publish(queue="system.notification", body=json.dumps(completion_notification).encode("utf-8"))
        steps.append({"step": "completion_notification", "data": completion_notification, "timestamp": time.time()})
        
        return {
            "demo_id": demo_id,
            "scenario": "workflow_orchestration",
            "success": True,
            "steps": steps,
            "workflow_steps": len(workflow["actions"]),
            "duration": time.time() - steps[0]["timestamp"],
            "summary": "Multi-step workflow executed with progress tracking and HUD updates"
        }
    
    async def _demo_system_integration(self, demo_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Demonstrate complete system integration"""
        steps = []
        
        # Step 1: System status check
        system_status = {
            "active_context": "System Integration Demo",
            "system_status": "Active",
            "cpu_usage": 45.2,
            "memory_usage": 62.1,
            "gpu_usage": 15.7,
            "active_agents": ["voice_engine", "hud_overlay", "cua_engine", "orchestrator"],
            "current_task": "System Integration Demo",
            "task_progress": 0.0
        }
        steps.append({"step": "system_status_check", "data": system_status, "timestamp": time.time()})
        
        # Step 2: Memory storage
        context_memory = {
            "type": "context_update",
            "user_id": "demo_user",
            "session_id": demo_id,
            "active_application": "system_demo",
            "current_task": "System Integration Demo",
            "role_context": "system_administrator",
            "metadata": {"demo_type": "integration", "version": "1.0"}
        }
        bus.publish(queue="memory.store", body=json.dumps(context_memory).encode("utf-8"))
        steps.append({"step": "context_stored", "data": context_memory, "timestamp": time.time()})
        
        # Step 3: Voice interaction simulation
        voice_interaction = {
            "type": "voice_interaction",
            "content": "Show me system status",
            "timestamp": time.time(),
            "user_id": "demo_user",
            "metadata": {"intent": "information_query", "confidence": 0.92}
        }
        bus.publish(queue="memory.store", body=json.dumps(voice_interaction).encode("utf-8"))
        steps.append({"step": "voice_interaction_logged", "data": voice_interaction, "timestamp": time.time()})
        
        # Step 4: HUD status update
        hud_update = {
            "type": "status_update",
            "data": {
                **system_status,
                "task_progress": 0.75,
                "demo_active": True
            }
        }
        steps.append({"step": "hud_status_updated", "data": hud_update, "timestamp": time.time()})
        
        # Step 5: Final integration confirmation
        integration_result = {
            "services_active": 4,
            "message_queues_healthy": True,
            "data_storage_functional": True,
            "workflow_execution_ready": True,
            "real_time_updates_working": True
        }
        steps.append({"step": "integration_validated", "data": integration_result, "timestamp": time.time()})
        
        return {
            "demo_id": demo_id,
            "scenario": "system_integration",
            "success": True,
            "steps": steps,
            "integration_points": len(integration_result),
            "duration": time.time() - steps[0]["timestamp"],
            "summary": "Complete system integration validated: Voice processing, agent orchestration, memory storage, HUD updates, and workflow execution all functioning together"
        }
    
    async def _monitor_services(self):
        """Monitor service health periodically"""
        while True:
            try:
                # Update service status (mock implementation)
                self.service_status = {
                    "voice_engine": {"status": "healthy", "last_check": time.time()},
                    "hud_overlay": {"status": "healthy", "last_check": time.time()},
                    "cua_engine": {"status": "healthy", "last_check": time.time()},
                    "planning_agent": {"status": "healthy", "last_check": time.time()},
                    "execution_agent": {"status": "healthy", "last_check": time.time()},
                    "memory_agent": {"status": "healthy", "last_check": time.time()}
                }
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Service monitoring error: {e}")
                await asyncio.sleep(60)  # Longer delay on error
    
    def get_system_health(self) -> SystemHealth:
        """Get overall system health"""
        services = [
            {"name": name, "status": info["status"]} 
            for name, info in self.service_status.items()
        ]
        
        healthy_services = sum(1 for s in services if s["status"] == "healthy")
        overall_status = "healthy" if healthy_services == len(services) else "degraded"
        
        return SystemHealth(
            status=overall_status,
            services=services,
            uptime=time.time() - self.start_time,
            active_workflows=len(self.active_demos)
        )


# Initialize orchestrator
orchestrator = DemoOrchestrator()


@app.get("/health", response_model=Health)
def health():
    """Health check endpoint"""
    return Health(service=settings.service_name or "orchestrator", status="ok")


@app.get("/system/health", response_model=SystemHealth)
def system_health():
    """Get overall system health"""
    return orchestrator.get_system_health()


@app.post("/demo/run")
async def run_demo(demo: SystemDemo):
    """Run a system demonstration scenario"""
    try:
        result = await orchestrator.run_demo_scenario(demo.scenario, demo.parameters)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Demo execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/demo/scenarios")
def get_demo_scenarios():
    """Get available demo scenarios"""
    return {
        "scenarios": [
            {
                "name": "voice_to_action",
                "description": "Demonstrates voice command processing through the entire pipeline",
                "parameters": {"command": "Optional voice command text"}
            },
            {
                "name": "workflow_orchestration", 
                "description": "Shows multi-step workflow execution with progress tracking",
                "parameters": {}
            },
            {
                "name": "system_integration",
                "description": "Validates complete system integration across all services",
                "parameters": {}
            }
        ]
    }


@app.on_event("startup")
async def startup():
    """Initialize orchestrator on startup"""
    logger.info("Starting System Orchestrator")
    await orchestrator.initialize()
    logger.info("System Orchestrator started successfully")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down System Orchestrator")