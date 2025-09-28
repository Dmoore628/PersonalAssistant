"""
HUD Overlay Service for Archi AI Digital Twin
Manages transparent desktop overlay, notifications, and status display
This is a mock implementation - real implementation would use DirectX 12 + ImGui on Windows
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
import time

from archi_core import Health, MessageBus, Settings
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .overlay_manager import OverlayManager
from .notification_system import NotificationSystem

settings = Settings()
app = FastAPI(title="HUD Overlay")
bus = MessageBus(url=settings.rabbitmq_url)

# Initialize overlay components
overlay_manager = OverlayManager()
notification_system = NotificationSystem()

logger = logging.getLogger(__name__)


class HUDStatus(BaseModel):
    """HUD status information"""
    active_context: str
    system_status: str
    cpu_usage: float
    gpu_usage: float
    current_task: Optional[str] = None
    task_progress: Optional[float] = None


class Notification(BaseModel):
    """Notification structure"""
    id: str
    title: str
    message: str
    type: str = "info"  # info, warning, error, success
    duration: int = 5000  # milliseconds
    priority: int = 1  # 1-5, higher is more important
    timestamp: float


@app.get("/health", response_model=Health)
def health():
    """Health check endpoint"""
    return Health(service=settings.service_name or "hud-overlay", status="ok")


@app.websocket("/ws/hud")
async def hud_websocket(websocket: WebSocket):
    """WebSocket endpoint for HUD updates"""
    await websocket.accept()
    logger.info("HUD WebSocket connection established")
    
    try:
        # Start overlay rendering
        await overlay_manager.start_rendering()
        
        # Send initial status
        status = await _get_system_status()
        await websocket.send_text(json.dumps({
            "type": "status_update",
            "data": status.dict()
        }))
        
        while True:
            # Wait for updates or commands
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "update_request":
                    # Send updated status
                    status = await _get_system_status()
                    await websocket.send_text(json.dumps({
                        "type": "status_update", 
                        "data": status.dict()
                    }))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket message error: {e}")
                
    except WebSocketDisconnect:
        logger.info("HUD WebSocket disconnected")
    except Exception as e:
        logger.error(f"HUD WebSocket error: {e}")
    finally:
        await overlay_manager.stop_rendering()


@app.post("/hud/notification")
async def create_notification(notification: Notification):
    """Create new HUD notification"""
    try:
        await notification_system.show_notification(notification)
        return {"status": "success", "notification_id": notification.id}
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        return {"status": "error", "error": str(e)}


@app.delete("/hud/notification/{notification_id}")
async def dismiss_notification(notification_id: str):
    """Dismiss HUD notification"""
    try:
        await notification_system.dismiss_notification(notification_id)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error dismissing notification: {e}")
        return {"status": "error", "error": str(e)}


@app.get("/hud/status")
async def get_hud_status():
    """Get current HUD status"""
    try:
        status = await _get_system_status()
        return status.dict()
    except Exception as e:
        logger.error(f"Error getting HUD status: {e}")
        return {"error": str(e)}


async def _get_system_status() -> HUDStatus:
    """Get current system status for HUD display"""
    # Mock system status (replace with real system monitoring)
    return HUDStatus(
        active_context="Development Mode",
        system_status="Active",
        cpu_usage=45.2,
        gpu_usage=12.8,
        current_task="Voice Engine Development",
        task_progress=0.65
    )


def _handle_task_progress(body: bytes):
    """Handle task progress updates"""
    try:
        data = json.loads(body)
        logger.info(f"Task progress update: {data}")
        
        # Update HUD display
        asyncio.create_task(_update_hud_task_progress(data))
        
    except Exception as e:
        logger.error(f"Error handling task progress: {e}")


async def _update_hud_task_progress(data: Dict[str, Any]):
    """Update HUD with task progress"""
    try:
        # Update overlay with new task information
        await overlay_manager.update_task_display(data)
        
    except Exception as e:
        logger.error(f"Error updating HUD task progress: {e}")


def _handle_system_notification(body: bytes):
    """Handle system notifications"""
    try:
        data = json.loads(body)
        logger.info(f"System notification: {data}")
        
        # Create notification
        notification = Notification(
            id=data.get("id", str(time.time())),
            title=data.get("title", "System Notification"),
            message=data.get("message", ""),
            type=data.get("type", "info"),
            priority=data.get("priority", 1)
        )
        
        asyncio.create_task(notification_system.show_notification(notification))
        
    except Exception as e:
        logger.error(f"Error handling system notification: {e}")


@app.on_event("startup")
async def startup():
    """Initialize HUD overlay on startup"""
    logger.info("Starting HUD Overlay Service")
    
    # Initialize components
    await overlay_manager.initialize()
    await notification_system.initialize()
    
    # Start consuming messages
    bus.consume_in_background("task.progress", _handle_task_progress)
    bus.consume_in_background("system.notification", _handle_system_notification)
    
    logger.info("HUD Overlay Service started successfully")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down HUD Overlay Service")
    await overlay_manager.cleanup()
    await notification_system.cleanup()