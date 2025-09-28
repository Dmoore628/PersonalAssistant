import uuid
from datetime import datetime, timezone
from typing import Optional

from archi_core import Health, Settings, ToolCreationRequest, logger
from fastapi import FastAPI, HTTPException

settings = Settings()
app = FastAPI(
    title="Archi Tool Creation Agent",
    description="Dynamic tool and automation script generation service",
    version="1.0.0",
)

# In-memory tool registry
tool_registry: dict[str, dict] = {}


@app.get("/health", response_model=Health)
def health():
    return Health(
        service=settings.service_name or "tool-creation-agent",
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@app.post("/tools/create")
def create_tool(request: ToolCreationRequest):
    """Create a new tool based on the specification."""
    try:
        tool_id = str(uuid.uuid4())

        # Generate tool based on template type
        if request.template_type == "script":
            tool_content = generate_script_tool(request)
        elif request.template_type == "automation":
            tool_content = generate_automation_tool(request)
        elif request.template_type == "integration":
            tool_content = generate_integration_tool(request)
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported template type: {request.template_type}"
            )

        # Validate the generated tool
        validation_result = validate_tool(tool_content, request.safety_level)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, detail=f"Tool validation failed: {validation_result['errors']}"
            )

        # Store the tool
        tool_data = {
            "id": tool_id,
            "name": request.name,
            "description": request.description,
            "template_type": request.template_type,
            "target_application": request.target_application,
            "safety_level": request.safety_level,
            "content": tool_content,
            "parameters": request.parameters,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "validation": validation_result,
            "usage_count": 0,
        }

        tool_registry[tool_id] = tool_data

        logger.info(f"Created new tool: {request.name} (ID: {tool_id})")

        return {
            "tool_id": tool_id,
            "name": request.name,
            "status": "created",
            "validation": validation_result,
            "preview": tool_content[:500] + "..." if len(tool_content) > 500 else tool_content,
        }

    except Exception as e:
        logger.error(f"Failed to create tool: {e}")
        raise HTTPException(status_code=500, detail=f"Tool creation failed: {e!s}") from e


@app.get("/tools/{tool_id}")
def get_tool(tool_id: str):
    """Retrieve a specific tool by ID."""
    if tool_id not in tool_registry:
        raise HTTPException(status_code=404, detail="Tool not found")

    return tool_registry[tool_id]


@app.get("/tools")
def list_tools(template_type: Optional[str] = None, limit: int = 50):
    """List all created tools with optional filtering."""
    tools = list(tool_registry.values())

    if template_type:
        tools = [tool for tool in tools if tool["template_type"] == template_type]

    # Sort by creation date (most recent first)
    tools.sort(key=lambda x: x["created_at"], reverse=True)

    return {"tools": tools[:limit], "total": len(tools)}


@app.post("/tools/{tool_id}/execute")
def execute_tool(tool_id: str, execution_parameters: Optional[dict] = None):
    """Execute a created tool (simulation)."""
    if tool_id not in tool_registry:
        raise HTTPException(status_code=404, detail="Tool not found")

    tool = tool_registry[tool_id]

    # Increment usage counter
    tool["usage_count"] += 1

    # Simulate tool execution
    execution_result = {
        "tool_id": tool_id,
        "tool_name": tool["name"],
        "status": "executed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": execution_parameters or {},
        "result": f"Tool '{tool['name']}' executed successfully",
        "execution_time": 1.25,  # Simulated execution time
    }

    logger.info(f"Executed tool: {tool['name']} (ID: {tool_id})")

    return execution_result


@app.delete("/tools/{tool_id}")
def delete_tool(tool_id: str):
    """Delete a tool from the registry."""
    if tool_id not in tool_registry:
        raise HTTPException(status_code=404, detail="Tool not found")

    tool_name = tool_registry[tool_id]["name"]
    del tool_registry[tool_id]

    logger.info(f"Deleted tool: {tool_name} (ID: {tool_id})")

    return {"message": f"Tool '{tool_name}' deleted successfully"}


def generate_script_tool(request: ToolCreationRequest) -> str:
    """Generate a script-based tool."""
    # This is a simplified template generator
    # In production, this would use LLM integration for intelligent code generation

    script_template = f'''#!/usr/bin/env python3
"""
Generated Tool: {request.name}
Description: {request.description}
Created: {datetime.now(timezone.utc).isoformat()}
Safety Level: {request.safety_level}
"""

import sys
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main execution function for {request.name}.
    
    Args:
        parameters: Input parameters for the tool
        
    Returns:
        Dictionary containing execution results
    """
    try:
        logger.info(f"Starting execution of {request.name}")
        
        # Tool-specific logic would go here
        # This is a template that would be customized based on the request
        
        if parameters is None:
            parameters = {{}}
            
        # Example parameter processing
        target = parameters.get("target", "default")
        action = parameters.get("action", "process")
        
        logger.info(f"Processing {{action}} on {{target}}")
        
        # Simulate tool execution
        result = {{
            "status": "success",
            "message": f"Tool {request.name} executed successfully",
            "target": target,
            "action": action,
            "processed_items": 1
        }}
        
        logger.info("Tool execution completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Tool execution failed: {{e}}")
        return {{
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }}

if __name__ == "__main__":
    # Command line interface
    import json
    
    # Parse command line parameters
    params = {{}}
    if len(sys.argv) > 1:
        try:
            params = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            logger.error("Invalid JSON parameters provided")
            sys.exit(1)
    
    # Execute the tool
    result = main(params)
    
    # Output results
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("status") == "success" else 1)
'''
    
    return script_template


def generate_automation_tool(request: ToolCreationRequest) -> str:
    """Generate an automation workflow tool."""
    automation_template = f"""# Automation Tool: {request.name}
# Description: {request.description}
# Target Application: {request.target_application or "Generic"}
# Created: {datetime.now(timezone.utc).isoformat()}

# This is a workflow automation specification
# In production, this would generate actual automation scripts

workflow:
  name: "{request.name}"
  description: "{request.description}"
  target_application: "{request.target_application or 'generic'}"
  safety_level: "{request.safety_level}"
  
  steps:
    - name: "Initialize"
      action: "prepare_environment"
      parameters:
        validation_required: {request.safety_level in ['medium', 'high']}
        
    - name: "Execute Primary Task"
      action: "perform_automation"
      parameters:
        target: "{request.target_application or 'system'}"
        safety_checks: true
        
    - name: "Validate Results"
      action: "verify_completion"
      parameters:
        rollback_on_failure: true
        
    - name: "Cleanup"
      action: "finalize"
      parameters:
        preserve_logs: true

  error_handling:
    - condition: "validation_failed"
      action: "rollback"
      
    - condition: "permission_denied"
      action: "request_elevation"
      
    - condition: "timeout"
      action: "retry_with_backoff"

  parameters:
"""

    # Add custom parameters
    for param_name, param_value in request.parameters.items():
        automation_template += f"    {param_name}: {param_value}\n"

    return automation_template


def generate_integration_tool(request: ToolCreationRequest) -> str:
    """Generate an API integration tool."""
    integration_template = f'''"""
Integration Tool: {request.name}
Description: {request.description}
Target Application: {request.target_application or "Generic API"}
Created: {datetime.now(timezone.utc).isoformat()}
"""

import requests
import json
from typing import Dict, Any, Optional

class {request.name.replace(' ', '').replace('-', '')}Integration:
    """Integration class for {request.target_application or 'Generic API'}."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.example.com"
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({{"Authorization": f"Bearer {{self.api_key}}"}})
    
    def connect(self) -> bool:
        """Test connection to the API."""
        try:
            response = self.session.get(f"{{self.base_url}}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    def execute_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific operation."""
        endpoint_map = {{
            "create": "/create",
            "read": "/read",
            "update": "/update",
            "delete": "/delete",
            "list": "/list"
        }}
        
        endpoint = endpoint_map.get(operation, f"/{{operation}}")
        
        try:
            if operation in ["create", "update"]:
                response = self.session.post(f"{{self.base_url}}{{endpoint}}", json=parameters)
            elif operation == "delete":
                response = self.session.delete(f"{{self.base_url}}{{endpoint}}", params=parameters)
            else:
                response = self.session.get(f"{{self.base_url}}{{endpoint}}", params=parameters)
            
            response.raise_for_status()
            
            return {{
                "status": "success",
                "data": response.json() if response.content else {{}},
                "status_code": response.status_code
            }}
            
        except requests.RequestException as e:
            return {{
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__
            }}
    
    def batch_operation(self, operations: list) -> list:
        """Execute multiple operations in sequence."""
        results = []
        
        for op in operations:
            result = self.execute_operation(
                op.get("operation", "read"),
                op.get("parameters", {{}})
            )
            results.append(result)
            
            # Stop on first error if safety level is high
            if "{request.safety_level}" == "high" and result["status"] == "error":
                break
        
        return results

def main():
    """Main function for command-line usage."""
    integration = {request.name.replace(' ', '').replace('-', '')}Integration()
    
    if not integration.connect():
        print("Failed to connect to API")
        return 1
    
    # Example usage
    result = integration.execute_operation("list", {{}})
    print(json.dumps(result, indent=2))
    
    return 0 if result["status"] == "success" else 1

if __name__ == "__main__":
    exit(main())
'''
    
    return integration_template


def validate_tool(tool_content: str, safety_level: str) -> dict:
    """Validate generated tool for safety and correctness."""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "safety_score": 1.0,
    }

    # Check for dangerous patterns
    dangerous_patterns = [
        "rm -rf",
        "del /f /q",
        "format c:",
        "DROP TABLE",
        "DELETE FROM",
        "exec(",
        "eval(",
        "__import__",
        "subprocess.call",
        "os.system",
    ]

    content_lower = tool_content.lower()

    for pattern in dangerous_patterns:
        if pattern.lower() in content_lower:
            if safety_level == "high":
                validation_result["valid"] = False
                validation_result["errors"].append(f"Dangerous pattern detected: {pattern}")
            else:
                validation_result["warnings"].append(f"Potentially dangerous pattern: {pattern}")
            validation_result["safety_score"] -= 0.2

    # Check for proper error handling
    if "try:" not in content_lower or "except" not in content_lower:
        validation_result["warnings"].append("Missing error handling")
        validation_result["safety_score"] -= 0.1

    # Check for logging
    if "logging" not in content_lower and "logger" not in content_lower:
        validation_result["warnings"].append("Missing logging implementation")
        validation_result["safety_score"] -= 0.05

    # Ensure safety score doesn't go below 0
    validation_result["safety_score"] = max(0.0, validation_result["safety_score"])

    return validation_result
