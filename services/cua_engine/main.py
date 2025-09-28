"""
Computer Use Agent (CUA) Engine for Archi AI Digital Twin
Handles application control, screen analysis, and workflow automation
Mock implementation for cross-platform compatibility
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
import time

from archi_core import Health, MessageBus, Settings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .screen_analyzer import ScreenAnalyzer
from .application_controller import ApplicationController
from .workflow_executor import WorkflowExecutor

settings = Settings()
app = FastAPI(title="CUA Engine")
bus = MessageBus(url=settings.rabbitmq_url)

# Initialize CUA components
screen_analyzer = ScreenAnalyzer()
app_controller = ApplicationController()
workflow_executor = WorkflowExecutor()

logger = logging.getLogger(__name__)


class CUAAction(BaseModel):
    """CUA action structure"""
    action_type: str  # click, type, scroll, key_press, open_app, etc.
    parameters: Dict[str, Any]
    target: Optional[str] = None  # application or UI element target
    coordinates: Optional[Dict[str, int]] = None  # x, y coordinates if needed
    timeout: int = 30  # timeout in seconds


class CUAWorkflow(BaseModel):
    """CUA workflow structure"""
    id: str
    name: str
    description: str
    actions: List[CUAAction]
    retry_policy: Dict[str, Any] = {"max_retries": 3, "retry_delay": 1}


class CUAResult(BaseModel):
    """CUA execution result"""
    success: bool
    action_id: Optional[str] = None
    result_data: Dict[str, Any] = {}
    error_message: Optional[str] = None
    execution_time: float
    screenshot_url: Optional[str] = None


@app.get("/health", response_model=Health)
def health():
    """Health check endpoint"""
    return Health(service=settings.service_name or "cua-engine", status="ok")


@app.post("/cua/execute", response_model=CUAResult)
async def execute_action(action: CUAAction):
    """Execute a single CUA action"""
    start_time = time.time()
    
    try:
        logger.info(f"Executing CUA action: {action.action_type}")
        
        # Analyze screen if needed
        if action.action_type in ["click", "type", "scroll"]:
            screen_info = await screen_analyzer.analyze_current_screen()
            action.parameters["screen_context"] = screen_info
        
        # Execute the action
        result = await app_controller.execute_action(action)
        
        execution_time = time.time() - start_time
        
        return CUAResult(
            success=True,
            action_id=str(time.time()),
            result_data=result,
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"CUA action execution failed: {e}")
        
        return CUAResult(
            success=False,
            error_message=str(e),
            execution_time=execution_time
        )


@app.post("/cua/workflow", response_model=CUAResult)
async def execute_workflow(workflow: CUAWorkflow):
    """Execute a CUA workflow"""
    start_time = time.time()
    
    try:
        logger.info(f"Executing CUA workflow: {workflow.name}")
        
        result = await workflow_executor.execute_workflow(workflow)
        
        execution_time = time.time() - start_time
        
        return CUAResult(
            success=True,
            result_data=result,
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"CUA workflow execution failed: {e}")
        
        return CUAResult(
            success=False,
            error_message=str(e),
            execution_time=execution_time
        )


@app.get("/cua/screen/analyze")
async def analyze_screen():
    """Analyze current screen"""
    try:
        analysis = await screen_analyzer.analyze_current_screen()
        return {"success": True, "analysis": analysis}
    except Exception as e:
        logger.error(f"Screen analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cua/applications")
async def get_applications():
    """Get list of available applications"""
    try:
        applications = await app_controller.get_available_applications()
        return {"success": True, "applications": applications}
    except Exception as e:
        logger.error(f"Failed to get applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _handle_system_execute(body: bytes):
    """Handle system execute commands from message bus"""
    try:
        data = json.loads(body)
        logger.info(f"System execute command: {data}")
        
        # Create CUA action from system command
        action = CUAAction(
            action_type=data.get("action", "unknown"),
            parameters=data.get("parameters", {}),
            target=data.get("target")
        )
        
        # Execute asynchronously
        asyncio.create_task(_execute_system_command(action, data.get("source")))
        
    except Exception as e:
        logger.error(f"Error handling system execute command: {e}")


async def _execute_system_command(action: CUAAction, source: str = "system"):
    """Execute system command and report results"""
    try:
        # Execute the action
        if action.action_type == "open_application":
            result = await app_controller.open_application(
                action.parameters.get("app_name", "")
            )
        elif action.action_type == "close_application":
            result = await app_controller.close_application(
                action.parameters.get("app_name", "")
            )
        else:
            result = await app_controller.execute_action(action)
        
        # Report success
        bus.publish(queue="system.result", body=json.dumps({
            "source": source,
            "action": action.action_type,
            "success": True,
            "result": result,
            "timestamp": time.time()
        }).encode("utf-8"))
        
    except Exception as e:
        logger.error(f"Error executing system command: {e}")
        
        # Report error
        bus.publish(queue="system.result", body=json.dumps({
            "source": source,
            "action": action.action_type,
            "success": False,
            "error": str(e),
            "timestamp": time.time()
        }).encode("utf-8"))


@app.on_event("startup")
async def startup():
    """Initialize CUA engine on startup"""
    logger.info("Starting CUA Engine")
    
    # Initialize components
    await screen_analyzer.initialize()
    await app_controller.initialize()
    await workflow_executor.initialize()
    
    # Start consuming system execute commands
    bus.consume_in_background("system.execute", _handle_system_execute)
    
    logger.info("CUA Engine started successfully")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down CUA Engine")
    await screen_analyzer.cleanup()
    await app_controller.cleanup()
    await workflow_executor.cleanup()