import uuid
from datetime import datetime, timezone
from typing import Optional

from archi_core import Health, Settings, logger
from fastapi import FastAPI, HTTPException

settings = Settings()
app = FastAPI(
    title="Archi HUD Overlay Agent",
    description="Windows HUD overlay service for real-time information display",
    version="1.0.0",
)

# HUD state management
overlay_active = False
overlay_elements = []
connected_hud_clients = []
overlay_config = {
    "position": "top-right",
    "transparency": 0.8,
    "size": {"width": 400, "height": 300},
    "theme": "dark",
}


@app.get("/health", response_model=Health)
def health():
    return Health(
        service=settings.service_name or "hud-overlay-agent",
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@app.post("/hud/toggle")
def toggle_overlay(enabled: bool):
    """Enable or disable the HUD overlay."""
    global overlay_active
    overlay_active = enabled

    logger.info(f"HUD overlay {'enabled' if enabled else 'disabled'}")

    return {
        "overlay_active": overlay_active,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/hud/status")
def get_overlay_status():
    """Get current HUD overlay status and configuration."""
    return {
        "overlay_active": overlay_active,
        "elements_count": len(overlay_elements),
        "connected_clients": len(connected_hud_clients),
        "config": overlay_config,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/hud/elements")
def add_overlay_element(
    element_type: str,
    content: str,
    position: Optional[dict] = None,
    style: Optional[dict] = None,
    duration: Optional[int] = None,
):
    """Add an element to the HUD overlay."""
    try:
        element_id = str(uuid.uuid4())

        element = {
            "id": element_id,
            "type": element_type,
            "content": content,
            "position": position or {"x": 10, "y": 10},
            "style": style or {"color": "#ffffff", "font_size": 14},
            "duration": duration,  # seconds, None for persistent
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,
        }

        if duration:
            from datetime import timedelta

            expires_at = datetime.now(timezone.utc) + timedelta(seconds=duration)
            element["expires_at"] = expires_at.isoformat()

        overlay_elements.append(element)

        logger.info(f"Added HUD element: {element_type} - {content[:50]}...")

        return element

    except Exception as e:
        logger.error(f"Failed to add HUD element: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add element: {e!s}") from e


@app.post("/hud/notifications")
def show_notification(
    title: str,
    message: str,
    notification_type: str = "info",
    duration: int = 5,
):
    """Show a notification on the HUD overlay."""
    try:
        element = add_overlay_element(
            element_type="notification",
            content=f"{title}: {message}",
            position={"x": 20, "y": 50},
            style={
                "color": get_notification_color(notification_type),
                "font_size": 16,
            },
            duration=duration,
        )

        logger.info(f"Showing notification: {title} - {message}")

        return element

    except Exception as e:
        logger.error(f"Failed to show notification: {e}")
        raise HTTPException(status_code=500, detail=f"Notification failed: {e!s}") from e


def get_notification_color(notification_type: str) -> str:
    """Get color for notification type."""
    colors = {
        "info": "#2196f3",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
    }
    return colors.get(notification_type, "#2196f3")
