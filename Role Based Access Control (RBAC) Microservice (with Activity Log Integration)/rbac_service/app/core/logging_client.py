# app/core/logging_client.py
import httpx
import os
from typing import Optional, Dict, Any
import logging # Use standard Python logging for errors here

# Configure logging for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Get the Activity Log Service URL from environment variable or use a default
# IMPORTANT: Replace 'activity-logs' with the actual service name from Team 9's docker-compose.yml
# Consider managing this via your main settings (app/core/config.py) instead.
ACTIVITY_LOG_SERVICE_URL = os.getenv("ACTIVITY_LOG_SERVICE_URL", "http://activity-logs-service:3000/api/activities")


# Define constants for your RBAC actions
ACTION_CREATE_ROLE = "CREATE_ROLE"
ACTION_UPDATE_ROLE = "UPDATE_ROLE"
ACTION_DELETE_ROLE = "DELETE_ROLE"
ACTION_CREATE_PERMISSION = "CREATE_PERMISSION"
ACTION_UPDATE_PERMISSION = "UPDATE_PERMISSION"
ACTION_DELETE_PERMISSION = "DELETE_PERMISSION"
ACTION_ASSIGN_PERMISSION_TO_ROLE = "ASSIGN_PERMISSION_TO_ROLE"
ACTION_REMOVE_PERMISSION_FROM_ROLE = "REMOVE_PERMISSION_FROM_ROLE"
ACTION_ASSIGN_ROLE_TO_USER = "ASSIGN_ROLE_TO_USER"
ACTION_REMOVE_ROLE_FROM_USER = "REMOVE_ROLE_FROM_USER"
ACTION_CHECK_PERMISSION = "CHECK_PERMISSION"

# Map RBAC actions to the enum values Team 9 expects, if possible
# If an exact match isn't available, use 'other' and put details in the 'details' field.
# Consult Team 9's enum: ['login', 'logout', 'profile_update', 'password_change', 'account_creation', 'account_deletion', 'permission_change', 'failed_login', 'other']
ACTION_MAP = {
    ACTION_CREATE_ROLE: "other",
    ACTION_UPDATE_ROLE: "other",
    ACTION_DELETE_ROLE: "other",
    ACTION_CREATE_PERMISSION: "other",
    ACTION_UPDATE_PERMISSION: "permission_change", # Matches Team 9's enum
    ACTION_DELETE_PERMISSION: "other",
    ACTION_ASSIGN_PERMISSION_TO_ROLE: "permission_change", # Matches Team 9's enum
    ACTION_REMOVE_PERMISSION_FROM_ROLE: "permission_change", # Matches Team 9's enum
    ACTION_ASSIGN_ROLE_TO_USER: "other",
    ACTION_REMOVE_ROLE_FROM_USER: "other",
    ACTION_CHECK_PERMISSION: "other",
}

async def log_activity(
    action: str,
    user_id: Optional[str] = "SYSTEM", # Default to SYSTEM if no specific user involved
    status: str = "success", # 'success' or 'failure'
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Sends a log entry to the Activity Log service."""

    mapped_action = ACTION_MAP.get(action, "other")

    payload = {
        "userId": user_id,
        "action": mapped_action,
        "status": status,
        "resourceType": resource_type,
        "resourceId": str(resource_id) if resource_id else None,
        "details": details or {}
    }
    if mapped_action == "other":
         payload["details"]["rbac_action"] = action # Add specific action if using 'other'

    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ACTIVITY_LOG_SERVICE_URL, json=payload, timeout=5.0)
            response.raise_for_status()
            logger.info(f"Activity logged successfully: {action} by {user_id} status {status}")
    except httpx.RequestError as exc:
        logger.error(f"Error sending log to Activity Service for action '{action}': {exc}")
    except httpx.HTTPStatusError as exc:
        logger.error(f"Activity Service returned error for action '{action}': {exc.response.status_code} - {exc.response.text}")
    except Exception as exc:
        logger.error(f"An unexpected error occurred during activity logging for action '{action}': {exc}")