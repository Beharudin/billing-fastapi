from fastapi import HTTPException

def require_roles(user, allowed_roles: list):

    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Not authorized for this action"
        )