"""
Workflow Executor for Computer Use Agent
Handles complex multi-step workflow execution with error handling and retry logic
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import time
import uuid

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Executes complex multi-step workflows"""
    
    def __init__(self):
        self.active_workflows = {}
        self.workflow_results = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize workflow executor"""
        try:
            logger.info("Initializing workflow executor")
            
            # Initialize workflow state management
            self.active_workflows = {}
            self.workflow_results = {}
            
            self.is_initialized = True
            logger.info("Workflow executor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize workflow executor: {e}")
            raise
    
    async def execute_workflow(self, workflow) -> Dict[str, Any]:
        """Execute a complete workflow"""
        if not self.is_initialized:
            raise ValueError("Workflow executor not initialized")
            
        workflow_id = workflow.id
        logger.info(f"Starting workflow execution: {workflow.name} ({workflow_id})")
        
        try:
            # Create workflow execution context
            execution_context = WorkflowExecutionContext(
                workflow_id=workflow_id,
                workflow=workflow,
                start_time=time.time()
            )
            
            # Track active workflow
            self.active_workflows[workflow_id] = execution_context
            
            # Execute workflow steps
            results = []
            for i, step in enumerate(workflow.actions):
                logger.info(f"Executing step {i+1}/{len(workflow.actions)}: {step.action_type}")
                
                try:
                    # Check dependencies
                    if not await self._check_step_dependencies(step, results):
                        raise Exception(f"Step dependencies not met: {step.dependencies}")
                    
                    # Execute step with retry logic
                    step_result = await self._execute_step_with_retry(step, execution_context)
                    step_result["step_index"] = i
                    step_result["step_id"] = getattr(step, 'id', f"step_{i}")
                    
                    results.append(step_result)
                    
                    # Check if step failed critically
                    if not step_result.get("success", False):
                        # Determine if workflow should continue
                        if step.parameters.get("critical", True):
                            raise Exception(f"Critical step failed: {step.action_type}")
                        else:
                            logger.warning(f"Non-critical step failed: {step.action_type}")
                    
                except Exception as e:
                    logger.error(f"Step execution failed: {e}")
                    results.append({
                        "step_index": i,
                        "step_id": getattr(step, 'id', f"step_{i}"),
                        "success": False,
                        "error": str(e),
                        "execution_time": 0
                    })
                    
                    # Stop workflow on critical failure
                    if step.parameters.get("critical", True):
                        break
            
            # Calculate overall success
            successful_steps = sum(1 for r in results if r.get("success", False))
            total_steps = len(results)
            success_rate = successful_steps / total_steps if total_steps > 0 else 0
            
            execution_time = time.time() - execution_context.start_time
            
            workflow_result = {
                "workflow_id": workflow_id,
                "workflow_name": workflow.name,
                "success": success_rate >= 0.8,  # 80% success threshold
                "success_rate": success_rate,
                "total_steps": total_steps,
                "successful_steps": successful_steps,
                "execution_time": execution_time,
                "step_results": results,
                "metadata": {
                    "start_time": execution_context.start_time,
                    "end_time": time.time(),
                    "retry_attempts": execution_context.total_retries
                }
            }
            
            # Store result
            self.workflow_results[workflow_id] = workflow_result
            
            # Remove from active workflows
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            logger.info(f"Workflow completed: {workflow.name} - Success: {workflow_result['success']} ({successful_steps}/{total_steps} steps)")
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            
            # Clean up
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            raise
    
    async def _execute_step_with_retry(self, step, execution_context: 'WorkflowExecutionContext') -> Dict[str, Any]:
        """Execute a single step with retry logic"""
        retry_policy = step.retry_policy
        max_retries = retry_policy.get("max_retries", 3)
        retry_delay = retry_policy.get("retry_delay", 1)
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                # Execute the step (mock implementation)
                result = await self._mock_step_execution(step)
                
                execution_time = time.time() - start_time
                
                result.update({
                    "success": True,
                    "attempt": attempt + 1,
                    "execution_time": execution_time
                })
                
                logger.info(f"Step executed successfully on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                last_error = e
                execution_context.total_retries += 1
                
                logger.warning(f"Step execution attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        # All attempts failed
        return {
            "success": False,
            "error": str(last_error),
            "attempts": max_retries + 1,
            "execution_time": 0
        }
    
    async def _mock_step_execution(self, step) -> Dict[str, Any]:
        """Mock step execution (replace with real implementation)"""
        action_type = step.action_type
        parameters = step.parameters
        
        # Simulate execution time
        await asyncio.sleep(0.1)
        
        # Mock different action types
        if action_type == "open_application":
            app_name = parameters.get("app_name", "unknown")
            return {
                "action": action_type,
                "app_name": app_name,
                "result": f"Opened {app_name}"
            }
        
        elif action_type == "click":
            x, y = parameters.get("x", 0), parameters.get("y", 0)
            return {
                "action": action_type,
                "coordinates": {"x": x, "y": y},
                "result": f"Clicked at ({x}, {y})"
            }
        
        elif action_type == "type":
            text = parameters.get("text", "")
            return {
                "action": action_type,
                "text": text,
                "result": f"Typed: {text}"
            }
        
        elif action_type == "wait":
            duration = parameters.get("duration", 1)
            await asyncio.sleep(duration)
            return {
                "action": action_type,
                "duration": duration,
                "result": f"Waited {duration} seconds"
            }
        
        else:
            return {
                "action": action_type,
                "result": f"Executed {action_type}"
            }
    
    async def _check_step_dependencies(self, step, previous_results: List[Dict[str, Any]]) -> bool:
        """Check if step dependencies are satisfied"""
        dependencies = getattr(step, 'dependencies', [])
        
        if not dependencies:
            return True
        
        # Check if all dependency steps completed successfully
        completed_step_ids = {
            result.get("step_id") for result in previous_results 
            if result.get("success", False)
        }
        
        for dependency in dependencies:
            if dependency not in completed_step_ids:
                logger.warning(f"Dependency not met: {dependency}")
                return False
        
        return True
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a running or completed workflow"""
        # Check if workflow is active
        if workflow_id in self.active_workflows:
            context = self.active_workflows[workflow_id]
            return {
                "workflow_id": workflow_id,
                "status": "running",
                "start_time": context.start_time,
                "current_step": getattr(context, 'current_step', 0),
                "total_steps": len(context.workflow.actions)
            }
        
        # Check if workflow is completed
        if workflow_id in self.workflow_results:
            result = self.workflow_results[workflow_id]
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "success": result["success"],
                "execution_time": result["execution_time"]
            }
        
        return None
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id in self.active_workflows:
            logger.info(f"Cancelling workflow: {workflow_id}")
            del self.active_workflows[workflow_id]
            return True
        
        return False
    
    async def cleanup(self):
        """Cleanup workflow executor"""
        try:
            logger.info("Cleaning up workflow executor")
            
            # Cancel all active workflows
            for workflow_id in list(self.active_workflows.keys()):
                await self.cancel_workflow(workflow_id)
            
            self.workflow_results.clear()
            self.is_initialized = False
            
            logger.info("Workflow executor cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during workflow executor cleanup: {e}")


class WorkflowExecutionContext:
    """Context for workflow execution"""
    
    def __init__(self, workflow_id: str, workflow, start_time: float):
        self.workflow_id = workflow_id
        self.workflow = workflow
        self.start_time = start_time
        self.current_step = 0
        self.total_retries = 0
        self.metadata = {}