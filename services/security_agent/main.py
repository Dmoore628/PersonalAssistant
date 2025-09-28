import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional

from archi_core import Health, SecurityAuditLog, Settings, logger
from fastapi import FastAPI, Request

settings = Settings()
app = FastAPI(
    title="Archi Security Agent",
    description="Security monitoring, access control, and audit logging service",
    version="1.0.0",
)

# In-memory audit log storage (in production, this would be a persistent database)
audit_logs: dict[str, SecurityAuditLog] = {}


@app.get("/health", response_model=Health)
def health():
    return Health(
        service=settings.service_name or "security-agent",
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@app.post("/audit/log", response_model=SecurityAuditLog)
def create_audit_log(
    event_type: str,
    action: str,
    result: str,
    user_role: Optional[str] = None,
    resource: Optional[str] = None,
    risk_level: str = "low",
    details: Optional[dict] = None,
):
    """Create a new security audit log entry."""
    log_entry = SecurityAuditLog(
        id=str(uuid.uuid4()),
        event_type=event_type,
        user_role=user_role,
        action=action,
        resource=resource,
        result=result,
        risk_level=risk_level,
        timestamp=datetime.now(timezone.utc).isoformat(),
        details=details or {},
    )

    audit_logs[log_entry.id] = log_entry

    # Log high-risk events for immediate attention
    if risk_level in ["high", "critical"]:
        logger.warning(f"High-risk security event: {event_type} - {action} - {result}")

    return log_entry


@app.get("/audit/logs")
def get_audit_logs(
    event_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 100,
):
    """Retrieve audit logs with optional filtering."""
    logs = list(audit_logs.values())

    # Apply filters
    if event_type:
        logs = [log for log in logs if log.event_type == event_type]

    if risk_level:
        logs = [log for log in logs if log.risk_level == risk_level]

    # Sort by timestamp (most recent first)
    logs.sort(key=lambda x: x.timestamp, reverse=True)

    return {"logs": logs[:limit], "total": len(logs)}


@app.post("/security/validate_action")
def validate_action(
    action: str,
    resource: str,
    user_role: Optional[str] = None,
    context: Optional[dict] = None,
):
    """Validate if an action is allowed based on security policies."""
    risk_score = calculate_risk_score(action, resource, user_role, context)

    # Define risk thresholds
    is_allowed = True
    requires_confirmation = False
    warnings = []

    if risk_score >= 0.8:
        is_allowed = False
        warnings.append("Action blocked due to high security risk")
    elif risk_score >= 0.6:
        requires_confirmation = True
        warnings.append("Action requires user confirmation")
    elif risk_score >= 0.4:
        warnings.append("Medium risk action detected")

    # Log the validation attempt
    create_audit_log(
        event_type="action_validation",
        action=action,
        result="allowed" if is_allowed else "blocked",
        user_role=user_role,
        resource=resource,
        risk_level=get_risk_level(risk_score),
        details={
            "risk_score": risk_score,
            "context": context or {},
        },
    )

    return {
        "allowed": is_allowed,
        "requires_confirmation": requires_confirmation,
        "risk_score": risk_score,
        "warnings": warnings,
    }


@app.post("/security/encrypt")
def encrypt_data(data: str, context: Optional[str] = None):
    """Encrypt sensitive data using SHA-256 (placeholder implementation)."""
    # In production, this would use proper encryption like AES-256
    # This is a simplified hash for demonstration
    salt = str(uuid.uuid4())
    encrypted = hashlib.sha256(f"{data}{salt}".encode()).hexdigest()

    create_audit_log(
        event_type="data_encryption",
        action="encrypt",
        result="success",
        resource=context,
        risk_level="low",
        details={"data_length": len(data)},
    )

    return {"encrypted_data": encrypted, "salt": salt}


@app.post("/security/scan_content")
def scan_content(content: str, content_type: str = "text"):
    """Scan content for security threats or sensitive information."""
    threats = []
    risk_level = "low"

    # Simple threat detection patterns
    threat_patterns = {
        "password": r"(?i)(password|pwd|pass)\s*[:=]\s*\w+",
        "api_key": r"(?i)(api[_-]?key|token)\s*[:=]\s*[a-zA-Z0-9_-]+",
        "sql_injection": r"(?i)(union|select|insert|delete|drop|exec)\s+",
        "xss": r"(?i)<script|javascript:|onclick=",
        "credential": r"(?i)(username|login|auth)\s*[:=]\s*\w+",
    }

    for threat_type, pattern in threat_patterns.items():
        import re

        if re.search(pattern, content):
            threats.append(threat_type)
            if threat_type in ["password", "api_key", "credential"]:
                risk_level = "high"
            elif threat_type in ["sql_injection", "xss"]:
                risk_level = "critical"

    # Log the scan results
    create_audit_log(
        event_type="content_scan",
        action="scan",
        result=f"threats_found: {len(threats)}",
        resource=content_type,
        risk_level=risk_level,
        details={
            "threats": threats,
            "content_length": len(content),
        },
    )

    return {
        "safe": len(threats) == 0,
        "threats": threats,
        "risk_level": risk_level,
        "recommendations": get_security_recommendations(threats),
    }


@app.get("/security/status")
def get_security_status():
    """Get overall security status and metrics."""
    recent_logs = [
        log
        for log in audit_logs.values()
        if (
            datetime.now(timezone.utc)
            - datetime.fromisoformat(log.timestamp.replace("Z", "+00:00"))
        ).total_seconds()
        < 3600
    ]

    risk_counts = {}
    for log in recent_logs:
        risk_counts[log.risk_level] = risk_counts.get(log.risk_level, 0) + 1

    return {
        "status": "healthy" if risk_counts.get("critical", 0) == 0 else "alert",
        "recent_events": len(recent_logs),
        "risk_distribution": risk_counts,
        "high_risk_threshold_exceeded": risk_counts.get("high", 0) + risk_counts.get("critical", 0)
        >= 5,
    }


def calculate_risk_score(
    action: str, resource: str, user_role: Optional[str], context: Optional[dict]
) -> float:
    """Calculate risk score for an action (0.0 = low risk, 1.0 = critical risk)."""
    score = 0.0

    # Base risk based on action type
    high_risk_actions = ["delete", "remove", "install", "uninstall", "execute", "modify_system"]
    medium_risk_actions = ["write", "create", "send", "publish", "transfer"]

    if any(risk_action in action.lower() for risk_action in high_risk_actions):
        score += 0.4
    elif any(risk_action in action.lower() for risk_action in medium_risk_actions):
        score += 0.2

    # Resource risk
    system_resources = ["system32", "program files", "registry", "services", "drivers"]
    if any(sys_res in resource.lower() for sys_res in system_resources):
        score += 0.3

    # User role considerations
    if user_role in ["admin", "system"]:
        score += 0.1  # Admins can do more but still need monitoring
    elif user_role in ["guest", "limited"]:
        score += 0.2  # Limited users doing risky actions is suspicious

    # Context-based risks
    if context:
        if context.get("external_request", False):
            score += 0.1
        if context.get("after_hours", False):
            score += 0.1
        if context.get("unusual_pattern", False):
            score += 0.2

    return min(score, 1.0)


def get_risk_level(score: float) -> str:
    """Convert risk score to categorical risk level."""
    if score >= 0.8:
        return "critical"
    if score >= 0.6:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def get_security_recommendations(threats: list[str]) -> list[str]:
    """Get security recommendations based on detected threats."""
    recommendations = []

    if "password" in threats or "credential" in threats:
        recommendations.append("Remove or mask sensitive credentials")
        recommendations.append("Use secure credential storage instead")

    if "api_key" in threats:
        recommendations.append("Store API keys in environment variables or secure vault")
        recommendations.append("Rotate API keys regularly")

    if "sql_injection" in threats:
        recommendations.append("Use parameterized queries")
        recommendations.append("Implement input validation")

    if "xss" in threats:
        recommendations.append("Sanitize user input")
        recommendations.append("Use Content Security Policy headers")

    return recommendations


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware to log and monitor all requests."""
    start_time = datetime.now()

    # Log the incoming request
    create_audit_log(
        event_type="api_request",
        action=f"{request.method} {request.url.path}",
        result="received",
        resource=str(request.url),
        risk_level="low",
        details={
            "method": request.method,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "ip": request.client.host if request.client else "unknown",
        },
    )

    response = await call_next(request)

    # Log the response
    processing_time = (datetime.now() - start_time).total_seconds()
    create_audit_log(
        event_type="api_response",
        action=f"{request.method} {request.url.path}",
        result=f"status_{response.status_code}",
        resource=str(request.url),
        risk_level="low" if response.status_code < 400 else "medium",
        details={
            "status_code": response.status_code,
            "processing_time": processing_time,
        },
    )

    return response
