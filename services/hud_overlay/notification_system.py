"""
Notification System for HUD Overlay
Handles notification display, queuing, and user interaction
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
import time
import uuid

logger = logging.getLogger(__name__)


class NotificationSystem:
    """Manages HUD notifications"""
    
    def __init__(self):
        self.active_notifications: Dict[str, 'NotificationItem'] = {}
        self.notification_queue: List['NotificationItem'] = []
        self.max_concurrent_notifications = 5
        self.is_running = False
        
    async def initialize(self):
        """Initialize notification system"""
        try:
            logger.info("Initializing notification system")
            
            # Start notification processing loop
            self.is_running = True
            asyncio.create_task(self._notification_processor())
            
            logger.info("Notification system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize notification system: {e}")
            raise
    
    async def show_notification(self, notification):
        """Display a new notification"""
        try:
            # Create notification item
            notification_item = NotificationItem(
                id=notification.id,
                title=notification.title,
                message=notification.message,
                type=notification.type,
                duration=notification.duration,
                priority=notification.priority,
                timestamp=time.time()
            )
            
            # Add to queue if at capacity, otherwise show immediately
            if len(self.active_notifications) >= self.max_concurrent_notifications:
                self.notification_queue.append(notification_item)
                logger.info(f"Notification queued: {notification.title}")
            else:
                await self._display_notification(notification_item)
                
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
            raise
    
    async def dismiss_notification(self, notification_id: str):
        """Dismiss a notification"""
        try:
            if notification_id in self.active_notifications:
                notification = self.active_notifications[notification_id]
                await self._hide_notification(notification)
                logger.info(f"Notification dismissed: {notification_id}")
            else:
                logger.warning(f"Notification not found for dismissal: {notification_id}")
                
        except Exception as e:
            logger.error(f"Error dismissing notification: {e}")
    
    async def _display_notification(self, notification: 'NotificationItem'):
        """Display notification in HUD"""
        try:
            # Add to active notifications
            self.active_notifications[notification.id] = notification
            notification.display_time = time.time()
            
            logger.info(f"Displaying notification: {notification.title} ({notification.type})")
            
            # Schedule auto-dismiss if duration is set
            if notification.duration > 0:
                asyncio.create_task(self._auto_dismiss_notification(notification))
                
        except Exception as e:
            logger.error(f"Error displaying notification: {e}")
    
    async def _hide_notification(self, notification: 'NotificationItem'):
        """Hide notification from HUD"""
        try:
            # Remove from active notifications
            if notification.id in self.active_notifications:
                del self.active_notifications[notification.id]
                
            # Process next in queue if available
            if self.notification_queue:
                next_notification = self.notification_queue.pop(0)
                await self._display_notification(next_notification)
                
            logger.info(f"Notification hidden: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error hiding notification: {e}")
    
    async def _auto_dismiss_notification(self, notification: 'NotificationItem'):
        """Auto-dismiss notification after duration"""
        try:
            # Wait for duration
            await asyncio.sleep(notification.duration / 1000)  # Convert ms to seconds
            
            # Check if still active
            if notification.id in self.active_notifications:
                await self._hide_notification(notification)
                
        except Exception as e:
            logger.error(f"Error in auto-dismiss: {e}")
    
    async def _notification_processor(self):
        """Background processor for notification management"""
        logger.info("Notification processor started")
        
        try:
            while self.is_running:
                # Process expired notifications
                current_time = time.time()
                expired_notifications = []
                
                for notification in self.active_notifications.values():
                    if (notification.duration > 0 and 
                        current_time - notification.display_time > notification.duration / 1000):
                        expired_notifications.append(notification)
                
                # Remove expired notifications
                for notification in expired_notifications:
                    await self._hide_notification(notification)
                
                # Process queue if space available
                while (len(self.active_notifications) < self.max_concurrent_notifications and 
                       self.notification_queue):
                    next_notification = self.notification_queue.pop(0)
                    await self._display_notification(next_notification)
                
                # Sleep before next processing cycle
                await asyncio.sleep(1.0)
                
        except Exception as e:
            logger.error(f"Notification processor error: {e}")
        finally:
            logger.info("Notification processor ended")
    
    async def get_active_notifications(self) -> List[Dict[str, Any]]:
        """Get list of active notifications"""
        return [notification.to_dict() for notification in self.active_notifications.values()]
    
    async def cleanup(self):
        """Cleanup notification system"""
        try:
            logger.info("Cleaning up notification system")
            
            self.is_running = False
            
            # Clear all notifications
            self.active_notifications.clear()
            self.notification_queue.clear()
            
            logger.info("Notification system cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during notification system cleanup: {e}")


class NotificationItem:
    """Individual notification item"""
    
    def __init__(self, id: str, title: str, message: str, type: str = "info", 
                 duration: int = 5000, priority: int = 1, timestamp: float = None):
        self.id = id
        self.title = title
        self.message = message
        self.type = type  # info, warning, error, success
        self.duration = duration  # milliseconds
        self.priority = priority  # 1-5, higher is more important
        self.timestamp = timestamp or time.time()
        self.display_time = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "duration": self.duration,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "display_time": self.display_time
        }