import uuid
from datetime import datetime, timezone
from typing import Optional

from archi_core import Health, LearningFeedback, Settings, logger
from fastapi import FastAPI, HTTPException

settings = Settings()
app = FastAPI(
    title="Archi Learning Agent",
    description="Human-in-the-loop learning and model adaptation service",
    version="1.0.0",
)

# In-memory learning data storage
feedback_history: dict[str, LearningFeedback] = {}
learning_patterns: dict[str, dict] = {}
user_preferences: dict[str, dict] = {}


@app.get("/health", response_model=Health)
def health():
    return Health(
        service=settings.service_name or "learning-agent",
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@app.post("/feedback/submit", response_model=LearningFeedback)
def submit_feedback(feedback: LearningFeedback):
    """Submit user feedback for a completed task."""
    try:
        # Store the feedback
        feedback_history[feedback.task_id] = feedback

        # Process the feedback for learning
        process_feedback(feedback)

        logger.info(f"Received feedback for task {feedback.task_id}: {feedback.feedback_type}")

        return feedback

    except Exception as e:
        logger.error(f"Failed to process feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback processing failed: {e!s}") from e


@app.get("/feedback/{task_id}", response_model=LearningFeedback)
def get_feedback(task_id: str):
    """Retrieve feedback for a specific task."""
    if task_id not in feedback_history:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return feedback_history[task_id]


@app.get("/learning/patterns")
def get_learning_patterns(user_role: Optional[str] = None, limit: int = 20):
    """Retrieve learned patterns and preferences."""
    patterns = dict(learning_patterns)

    if user_role:
        patterns = {k: v for k, v in patterns.items() if v.get("user_role") == user_role}

    # Sort by confidence score
    sorted_patterns = sorted(
        patterns.items(), key=lambda x: x[1].get("confidence", 0), reverse=True
    )

    return {
        "patterns": dict(sorted_patterns[:limit]),
        "total": len(patterns),
        "user_role": user_role,
    }


@app.get("/learning/preferences/{user_role}")
def get_user_preferences(user_role: str):
    """Get learned preferences for a specific user role."""
    if user_role not in user_preferences:
        return {"user_role": user_role, "preferences": {}, "learned_patterns": 0}

    return {
        "user_role": user_role,
        "preferences": user_preferences[user_role],
        "learned_patterns": len(
            [p for p in learning_patterns.values() if p.get("user_role") == user_role]
        ),
    }


@app.post("/learning/predict")
def predict_user_preference(
    context: dict,
    user_role: Optional[str] = None,
    task_type: Optional[str] = None,
):
    """Predict user preferences based on learned patterns."""
    try:
        # Find relevant patterns
        relevant_patterns = []

        for pattern_id, pattern in learning_patterns.items():
            # Match by user role
            if user_role and pattern.get("user_role") != user_role:
                continue

            # Match by task type
            if task_type and pattern.get("task_type") != task_type:
                continue

            # Check context similarity
            similarity_score = calculate_context_similarity(context, pattern.get("context", {}))
            if similarity_score > 0.3:  # Threshold for relevance
                relevant_patterns.append(
                    {
                        "pattern_id": pattern_id,
                        "pattern": pattern,
                        "similarity": similarity_score,
                    }
                )

        # Sort by similarity and confidence
        relevant_patterns.sort(
            key=lambda x: x["similarity"] * x["pattern"].get("confidence", 0), reverse=True
        )

        # Generate prediction
        if relevant_patterns:
            best_pattern = relevant_patterns[0]["pattern"]
            prediction = {
                "predicted_rating": best_pattern.get("avg_rating", 3),
                "confidence": best_pattern.get("confidence", 0.5)
                * relevant_patterns[0]["similarity"],
                "recommendation": best_pattern.get(
                    "recommendation", "Continue with current approach"
                ),
                "based_on_patterns": len(relevant_patterns),
            }
        else:
            # Default prediction when no patterns match
            prediction = {
                "predicted_rating": 3,
                "confidence": 0.1,
                "recommendation": "No specific preference learned yet",
                "based_on_patterns": 0,
            }

        return prediction

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e!s}") from e


@app.post("/learning/adapt")
def adapt_model(
    adaptation_type: str,
    parameters: dict,
    user_role: Optional[str] = None,
):
    """Adapt the learning model based on new insights."""
    try:
        adaptation_id = str(uuid.uuid4())

        if adaptation_type == "preference_update":
            update_user_preferences(parameters, user_role)
        elif adaptation_type == "pattern_refinement":
            refine_learning_patterns(parameters)
        elif adaptation_type == "confidence_adjustment":
            adjust_pattern_confidence(parameters)
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown adaptation type: {adaptation_type}"
            )

        logger.info(f"Model adapted: {adaptation_type} for user role {user_role}")

        return {
            "adaptation_id": adaptation_id,
            "type": adaptation_type,
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "parameters": parameters,
        }

    except Exception as e:
        logger.error(f"Model adaptation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Adaptation failed: {e!s}") from e


@app.get("/learning/insights")
def get_learning_insights():
    """Get insights about the learning process and effectiveness."""
    total_feedback = len(feedback_history)
    positive_feedback = len([f for f in feedback_history.values() if f.feedback_type == "positive"])
    negative_feedback = len([f for f in feedback_history.values() if f.feedback_type == "negative"])

    # Calculate learning effectiveness
    if total_feedback > 0:
        positive_ratio = positive_feedback / total_feedback
        learning_trend = "improving" if positive_ratio > 0.6 else "needs_attention"
    else:
        positive_ratio = 0.0
        learning_trend = "insufficient_data"

    # User role analysis
    role_feedback = {}
    for feedback in feedback_history.values():
        role = feedback.user_role or "unknown"
        if role not in role_feedback:
            role_feedback[role] = {"positive": 0, "negative": 0, "total": 0}

        role_feedback[role]["total"] += 1
        if feedback.feedback_type == "positive":
            role_feedback[role]["positive"] += 1
        elif feedback.feedback_type == "negative":
            role_feedback[role]["negative"] += 1

    return {
        "total_feedback_entries": total_feedback,
        "positive_feedback": positive_feedback,
        "negative_feedback": negative_feedback,
        "positive_ratio": positive_ratio,
        "learning_trend": learning_trend,
        "patterns_learned": len(learning_patterns),
        "user_roles_tracked": len(user_preferences),
        "role_performance": role_feedback,
        "insights": generate_learning_insights(role_feedback, learning_trend),
    }


def process_feedback(feedback: LearningFeedback):
    """Process feedback to extract learning patterns."""
    pattern_key = f"{feedback.user_role}_{feedback.context.get('task_type', 'general')}"

    if pattern_key not in learning_patterns:
        learning_patterns[pattern_key] = {
            "user_role": feedback.user_role,
            "task_type": feedback.context.get("task_type", "general"),
            "feedback_count": 0,
            "positive_count": 0,
            "negative_count": 0,
            "avg_rating": 0.0,
            "confidence": 0.0,
            "context": feedback.context,
            "recommendations": [],
        }

    pattern = learning_patterns[pattern_key]
    pattern["feedback_count"] += 1

    # Update counts
    if feedback.feedback_type == "positive":
        pattern["positive_count"] += 1
    elif feedback.feedback_type == "negative":
        pattern["negative_count"] += 1

    # Update average rating
    if feedback.rating:
        current_avg = pattern["avg_rating"]
        count = pattern["feedback_count"]
        pattern["avg_rating"] = ((current_avg * (count - 1)) + feedback.rating) / count

    # Update confidence based on feedback consistency
    if pattern["feedback_count"] >= 3:
        consistency = (
            max(pattern["positive_count"], pattern["negative_count"]) / pattern["feedback_count"]
        )
        pattern["confidence"] = min(consistency, 1.0)

    # Extract recommendations from feedback comments
    if feedback.comment and feedback.feedback_type == "positive":
        pattern["recommendations"].append(feedback.comment)
        # Keep only the most recent 5 recommendations
        pattern["recommendations"] = pattern["recommendations"][-5:]

    # Update user preferences
    if feedback.user_role:
        update_user_preferences_from_feedback(feedback)


def update_user_preferences_from_feedback(feedback: LearningFeedback):
    """Update user preferences based on feedback."""
    role = feedback.user_role
    if role not in user_preferences:
        user_preferences[role] = {
            "preferred_confirmation_level": "medium",
            "preferred_speed": "normal",
            "preferred_verbosity": "standard",
            "preferred_risk_tolerance": "medium",
        }

    prefs = user_preferences[role]

    # Adapt preferences based on feedback
    if (
        feedback.feedback_type == "negative"
        and "too slow" in (feedback.comment or "").lower()
        and prefs["preferred_speed"] == "normal"
    ):
        prefs["preferred_speed"] = "fast"
    elif (
        feedback.feedback_type == "negative"
        and "too fast" in (feedback.comment or "").lower()
        and prefs["preferred_speed"] == "normal"
    ):
        prefs["preferred_speed"] = "slow"

    # Adjust confirmation preferences
    if "confirm" in (feedback.comment or "").lower():
        if feedback.feedback_type == "positive":
            prefs["preferred_confirmation_level"] = "high"
        elif feedback.feedback_type == "negative":
            prefs["preferred_confirmation_level"] = "low"


def calculate_context_similarity(context1: dict, context2: dict) -> float:
    """Calculate similarity between two contexts."""
    if not context1 or not context2:
        return 0.0

    common_keys = set(context1.keys()) & set(context2.keys())
    if not common_keys:
        return 0.0

    matches = 0
    total = len(common_keys)

    for key in common_keys:
        if context1[key] == context2[key]:
            matches += 1

    return matches / total if total > 0 else 0.0


def update_user_preferences(parameters: dict, user_role: Optional[str]):
    """Update user preferences with new parameters."""
    if not user_role:
        return

    if user_role not in user_preferences:
        user_preferences[user_role] = {}

    user_preferences[user_role].update(parameters)


def refine_learning_patterns(parameters: dict):
    """Refine existing learning patterns."""
    pattern_id = parameters.get("pattern_id")
    if pattern_id and pattern_id in learning_patterns:
        learning_patterns[pattern_id].update(parameters.get("updates", {}))


def adjust_pattern_confidence(parameters: dict):
    """Adjust confidence scores for patterns."""
    pattern_id = parameters.get("pattern_id")
    new_confidence = parameters.get("confidence", 0.5)

    if pattern_id and pattern_id in learning_patterns:
        learning_patterns[pattern_id]["confidence"] = max(0.0, min(1.0, new_confidence))


def generate_learning_insights(role_feedback: dict, learning_trend: str) -> list[str]:
    """Generate actionable insights from learning data."""
    insights = []

    if learning_trend == "improving":
        insights.append("System is learning effectively from user feedback")
    elif learning_trend == "needs_attention":
        insights.append("High negative feedback ratio - review task execution strategies")
    else:
        insights.append("Insufficient feedback data - encourage more user interaction")

    # Role-specific insights
    for role, stats in role_feedback.items():
        if stats["total"] >= 5:  # Minimum feedback threshold
            positive_ratio = stats["positive"] / stats["total"]
            if positive_ratio < 0.4:
                insights.append(f"User role '{role}' showing low satisfaction - review preferences")
            elif positive_ratio > 0.8:
                insights.append(
                    f"User role '{role}' highly satisfied - replicate successful patterns"
                )

    return insights
