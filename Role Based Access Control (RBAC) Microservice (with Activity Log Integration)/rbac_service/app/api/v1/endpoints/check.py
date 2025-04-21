# app/api/v1/endpoints/check.py
# Add BackgroundTasks import
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
# No asyncio needed now

from app.db.session import get_db
from app.schemas.rbac import CheckRequest, CheckResponse
from app.core.security import check_user_permission
# Import the logging helper function and constant
from app.core.logging_client import log_activity, ACTION_CHECK_PERMISSION

router = APIRouter()

@router.post(
    "/check",
    response_model=CheckResponse,
    summary="Check User Permission",
    description="Check if a user has the specified permission based on their roles."
)
def check_permission_endpoint( # <--- Back to def
    *,
    db: Session = Depends(get_db),
    request_data: CheckRequest,
    background_tasks: BackgroundTasks # <--- Add BackgroundTasks dependency
) -> CheckResponse:
    allowed = check_user_permission(
        db=db,
        user_id=request_data.user_id,
        permission_name=request_data.permission
    )

    # --- (Optional) Log Check Result using BackgroundTasks ---
    background_tasks.add_task( # <--- Use add_task
        log_activity,
        action=ACTION_CHECK_PERMISSION,
        user_id=request_data.user_id,
        status="success" if allowed else "failure",
        resource_type="PermissionCheck",
        resource_id=request_data.permission,
        details={"result_allowed": allowed}
    )
    # ---------------------------------------------------------

    return CheckResponse(allowed=allowed)