from fastapi import FastAPI
from pydantic import BaseModel
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np

app = FastAPI(title="Computer Use Agent (CUA)")

class WindowAction(BaseModel):
    window_title: str
    action: str  # "focus", "minimize", "close"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/window_action")
def window_action(action: WindowAction):
    windows = gw.getWindowsWithTitle(action.window_title)
    if not windows:
        return {"error": "Window not found"}

    window = windows[0]
    if action.action == "focus":
        window.activate()
    elif action.action == "minimize":
        window.minimize()
    elif action.action == "close":
        window.close()
    else:
        return {"error": "Invalid action"}

    return {"message": f"Action {action.action} performed on {action.window_title}"}

@app.get("/screenshot")
def screenshot():
    screen = pyautogui.screenshot()
    screen_np = np.array(screen)
    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR))
    return {"screenshot": buffer.tobytes()}