"""
Voice Processing Engine for Archi AI Digital Twin
Handles wake-word detection, speech recognition, and text-to-speech
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any

from archi_core import Health, MessageBus, Settings
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .voice_processor import VoiceProcessor
from .audio_manager import AudioManager

settings = Settings()
app = FastAPI(title="Voice Engine")
bus = MessageBus(url=settings.rabbitmq_url)

# Initialize voice processing components
audio_manager = AudioManager()
voice_processor = VoiceProcessor()

logger = logging.getLogger(__name__)


class VoiceCommand(BaseModel):
    """Voice command structure"""
    text: str
    confidence: float
    intent: Optional[str] = None
    parameters: Dict[str, Any] = {}
    timestamp: float
    user_id: str = "default"


class VoiceResponse(BaseModel):
    """Voice response structure"""
    text: str
    audio_url: Optional[str] = None
    metadata: Dict[str, Any] = {}


@app.get("/health", response_model=Health)
def health():
    """Health check endpoint"""
    return Health(service=settings.service_name or "voice-engine", status="ok")


@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time voice processing"""
    await websocket.accept()
    logger.info("Voice WebSocket connection established")
    
    try:
        # Start audio processing
        await audio_manager.start_listening()
        
        while True:
            # Wait for audio data or commands
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "audio_chunk":
                # Process audio chunk
                audio_data = message.get("data")
                result = await voice_processor.process_audio_chunk(audio_data)
                
                if result:
                    await websocket.send_text(json.dumps({
                        "type": "transcription",
                        "data": result
                    }))
                    
            elif message.get("type") == "wake_word_detected":
                # Handle wake word detection
                logger.info("Wake word detected, starting full speech recognition")
                await websocket.send_text(json.dumps({
                    "type": "listening_active",
                    "data": {"status": "active"}
                }))
                
    except WebSocketDisconnect:
        logger.info("Voice WebSocket disconnected")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
    finally:
        await audio_manager.stop_listening()


@app.post("/voice/synthesize")
async def synthesize_speech(response: VoiceResponse):
    """Synthesize text to speech"""
    try:
        audio_url = await voice_processor.text_to_speech(
            text=response.text,
            metadata=response.metadata
        )
        return {"audio_url": audio_url, "status": "success"}
    except Exception as e:
        logger.error(f"Speech synthesis error: {e}")
        return {"error": str(e), "status": "failed"}


def _handle_voice_command(body: bytes):
    """Handle voice commands from message bus"""
    try:
        data = json.loads(body)
        command = VoiceCommand(**data)
        logger.info(f"Processing voice command: {command.text}")
        
        # Process the voice command and generate response
        asyncio.create_task(_process_command(command))
        
    except Exception as e:
        logger.error(f"Error handling voice command: {e}")


async def _process_command(command: VoiceCommand):
    """Process voice command and route to appropriate agent"""
    try:
        # Determine intent and route to appropriate agent
        if command.intent == "plan_task":
            # Route to planning agent
            bus.publish(queue="plan.created", body=json.dumps({
                "title": command.parameters.get("task", "Voice Command Task"),
                "description": command.text,
                "priority": command.parameters.get("priority", 3),
                "tags": ["voice_command"],
                "source": "voice_engine"
            }).encode("utf-8"))
            
        elif command.intent == "system_control":
            # Route to execution agent
            bus.publish(queue="system.execute", body=json.dumps({
                "action": command.parameters.get("action"),
                "parameters": command.parameters,
                "source": "voice_engine"
            }).encode("utf-8"))
            
        # Always log to memory agent
        bus.publish(queue="memory.store", body=json.dumps({
            "type": "voice_interaction",
            "content": command.text,
            "timestamp": command.timestamp,
            "user_id": command.user_id,
            "metadata": command.parameters
        }).encode("utf-8"))
        
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")


@app.on_event("startup")
async def startup():
    """Initialize voice engine on startup"""
    logger.info("Starting Voice Engine")
    
    # Initialize audio systems
    await audio_manager.initialize()
    await voice_processor.initialize()
    
    # Start consuming voice commands
    bus.consume_in_background("voice.command", _handle_voice_command)
    
    logger.info("Voice Engine started successfully")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down Voice Engine")
    await audio_manager.cleanup()
    await voice_processor.cleanup()