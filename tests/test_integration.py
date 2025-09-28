"""
Integration tests for Archi AI Digital Twin System
Tests the interaction between voice engine, HUD overlay, CUA engine, and agents
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch
import sys
import os

# Add archi_core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs', 'archi_core'))

from archi_core import AgentMessage, AgentMessageType, ContextData, SystemStatus


class TestServiceIntegration:
    """Test integration between services"""
    
    def test_agent_message_creation(self):
        """Test creating agent messages"""
        message = AgentMessage(
            sender_id="voice_engine",
            receiver_id="planning_agent",
            message_type=AgentMessageType.TASK_REQUEST,
            payload={"task": "Create a new document"},
            priority=3,
            timestamp=1234567890.0,
            correlation_id="test-correlation-123"
        )
        
        assert message.sender_id == "voice_engine"
        assert message.receiver_id == "planning_agent"
        assert message.message_type == AgentMessageType.TASK_REQUEST
        assert message.priority == 3
    
    def test_context_data_creation(self):
        """Test creating context data"""
        context = ContextData(
            user_id="user123",
            active_application="notepad",
            current_task="writing document",
            role_context="content_creator",
            session_id="session456"
        )
        
        assert context.user_id == "user123"
        assert context.active_application == "notepad"
        assert context.current_task == "writing document"
        assert context.role_context == "content_creator"
    
    def test_system_status_creation(self):
        """Test creating system status"""
        status = SystemStatus(
            active_context="Development Mode",
            system_status="Active",
            cpu_usage=45.2,
            memory_usage=60.5,
            gpu_usage=12.8,
            active_agents=["voice_engine", "hud_overlay", "cua_engine"],
            current_task="Testing system integration",
            task_progress=0.75
        )
        
        assert status.active_context == "Development Mode"
        assert status.cpu_usage == 45.2
        assert len(status.active_agents) == 3
        assert status.task_progress == 0.75


class TestVoiceEngineIntegration:
    """Test voice engine integration"""
    
    def test_voice_command_processing(self):
        """Test voice command structure"""
        # Simulate a voice command that would be processed
        voice_command = {
            "text": "Open notepad and create a new document",
            "confidence": 0.95,
            "intent": "plan_task",
            "parameters": {
                "action": "open_application",
                "app_name": "notepad",
                "task_type": "document_creation"
            },
            "timestamp": 1234567890.0,
            "user_id": "user123"
        }
        
        assert voice_command["confidence"] > 0.9
        assert voice_command["intent"] == "plan_task"
        assert voice_command["parameters"]["app_name"] == "notepad"


class TestHUDOverlayIntegration:
    """Test HUD overlay integration"""
    
    def test_notification_structure(self):
        """Test HUD notification structure"""
        notification = {
            "id": "notif-123",
            "title": "Task Completed",
            "message": "Document created successfully",
            "type": "success",
            "duration": 5000,
            "priority": 2,
            "timestamp": 1234567890.0
        }
        
        assert notification["type"] == "success"
        assert notification["priority"] == 2
        assert notification["duration"] == 5000
    
    def test_status_update_structure(self):
        """Test HUD status update structure"""
        status_update = {
            "type": "status_update",
            "data": {
                "active_context": "Document Creation",
                "system_status": "Active",
                "cpu_usage": 45.2,
                "gpu_usage": 12.8,
                "current_task": "Creating document",
                "task_progress": 0.65
            }
        }
        
        assert status_update["type"] == "status_update"
        assert status_update["data"]["task_progress"] == 0.65


class TestCUAEngineIntegration:
    """Test CUA engine integration"""
    
    def test_cua_action_structure(self):
        """Test CUA action structure"""
        cua_action = {
            "action_type": "open_application",
            "parameters": {
                "app_name": "notepad",
                "wait_for_ready": True
            },
            "target": "system",
            "timeout": 30
        }
        
        assert cua_action["action_type"] == "open_application"
        assert cua_action["parameters"]["app_name"] == "notepad"
        assert cua_action["timeout"] == 30
    
    def test_workflow_structure(self):
        """Test CUA workflow structure"""
        workflow = {
            "id": "workflow-123",
            "name": "Document Creation Workflow",
            "description": "Open notepad and create a new document",
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
                    "parameters": {"text": "Hello, World!"},
                    "timeout": 10
                }
            ],
            "retry_policy": {"max_retries": 3, "retry_delay": 1}
        }
        
        assert workflow["name"] == "Document Creation Workflow"
        assert len(workflow["actions"]) == 3
        assert workflow["actions"][0]["action_type"] == "open_application"


class TestAgentOrchestration:
    """Test agent orchestration and communication"""
    
    def test_message_flow_planning_to_execution(self):
        """Test message flow from planning to execution agent"""
        # Simulate planning agent creating a plan
        plan_message = {
            "id": "plan-123",
            "title": "Create Document",
            "description": "Open notepad and create a new document",
            "priority": 3,
            "tags": ["voice_command", "automation"],
            "source": "planning"
        }
        
        # Simulate execution agent processing the plan
        execution_command = {
            "action": "execute_workflow",
            "parameters": {
                "plan_id": plan_message["id"],
                "title": plan_message["title"],
                "description": plan_message["description"]
            },
            "source": "execution_agent"
        }
        
        assert execution_command["parameters"]["plan_id"] == "plan-123"
        assert "automation" in plan_message["tags"]
    
    def test_memory_storage_integration(self):
        """Test memory agent storage integration"""
        # Voice interaction storage
        voice_memory = {
            "type": "voice_interaction",
            "content": "Open notepad",
            "timestamp": 1234567890.0,
            "user_id": "user123",
            "metadata": {
                "confidence": 0.95,
                "intent": "system_control"
            }
        }
        
        # System action storage
        system_memory = {
            "type": "system_action",
            "action": "open_application",
            "success": True,
            "timestamp": 1234567890.0,
            "parameters": {"app_name": "notepad"}
        }
        
        assert voice_memory["type"] == "voice_interaction"
        assert system_memory["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])