"""
Audio Manager for Voice Processing Engine
Handles audio input/output, wake-word detection, and audio stream management
"""

import asyncio
import logging
from typing import Optional, Callable, Any
import json
import time

logger = logging.getLogger(__name__)


class AudioManager:
    """Manages audio input/output for the voice engine"""
    
    def __init__(self):
        self.is_listening = False
        self.wake_word_detector = None
        self.audio_stream = None
        self.callbacks = {}
        
    async def initialize(self):
        """Initialize audio systems"""
        try:
            logger.info("Initializing audio manager")
            
            # Initialize mock wake-word detector (replace with Picovoice Porcupine)
            self.wake_word_detector = MockWakeWordDetector()
            await self.wake_word_detector.initialize()
            
            logger.info("Audio manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize audio manager: {e}")
            raise
    
    async def start_listening(self):
        """Start audio listening and wake-word detection"""
        if self.is_listening:
            return
            
        try:
            logger.info("Starting audio listening")
            self.is_listening = True
            
            # Start wake-word detection
            asyncio.create_task(self._wake_word_detection_loop())
            
            logger.info("Audio listening started")
            
        except Exception as e:
            logger.error(f"Failed to start audio listening: {e}")
            raise
    
    async def stop_listening(self):
        """Stop audio listening"""
        if not self.is_listening:
            return
            
        try:
            logger.info("Stopping audio listening")
            self.is_listening = False
            
            if self.audio_stream:
                self.audio_stream.stop()
                
            logger.info("Audio listening stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop audio listening: {e}")
    
    async def _wake_word_detection_loop(self):
        """Continuous wake-word detection loop"""
        logger.info("Wake-word detection loop started")
        
        try:
            while self.is_listening:
                # Simulate audio processing
                await asyncio.sleep(0.1)  # 100ms chunks
                
                # Check for wake word (mock implementation)
                wake_detected = await self.wake_word_detector.process_audio_chunk()
                
                if wake_detected:
                    logger.info("Wake word detected!")
                    await self._handle_wake_word_detected()
                    
        except Exception as e:
            logger.error(f"Wake-word detection loop error: {e}")
        finally:
            logger.info("Wake-word detection loop ended")
    
    async def _handle_wake_word_detected(self):
        """Handle wake word detection"""
        try:
            # Trigger wake word callback
            if "wake_word" in self.callbacks:
                await self.callbacks["wake_word"]()
                
        except Exception as e:
            logger.error(f"Error handling wake word detection: {e}")
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for audio events"""
        self.callbacks[event] = callback
    
    async def cleanup(self):
        """Cleanup audio resources"""
        try:
            logger.info("Cleaning up audio manager")
            await self.stop_listening()
            
            if self.wake_word_detector:
                await self.wake_word_detector.cleanup()
                
            logger.info("Audio manager cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during audio cleanup: {e}")


class MockWakeWordDetector:
    """Mock wake-word detector for testing (replace with Picovoice Porcupine)"""
    
    def __init__(self):
        self.detection_count = 0
        self.last_detection = 0
        
    async def initialize(self):
        """Initialize mock detector"""
        logger.info("Mock wake-word detector initialized")
        
    async def process_audio_chunk(self) -> bool:
        """Process audio chunk and return True if wake word detected"""
        # Mock detection every 30 seconds for testing
        current_time = time.time()
        if current_time - self.last_detection > 30:
            self.last_detection = current_time
            self.detection_count += 1
            return True
        return False
        
    async def cleanup(self):
        """Cleanup detector resources"""
        logger.info("Mock wake-word detector cleanup complete")