"""
Hardened Role-Based Access Control (RBAC) & Token Guard
Enforces strict fail-closed authorization across sports platform routes.
"""
from functools import wraps
from typing import List

def require_roles(allowed_roles: List[str]):
    def decorator(fn):
        @wraps(fn)
        def wrapper(user_context: dict, *args, **kwargs):
            if not user_context or "role" not in user_context:
                raise PermissionError("HTTP 401: Unauthorized - Missing authentication token")
            user_role = user_context.get("role")
            if user_role not in allowed_roles:
                raise PermissionError(f"HTTP 403: Forbidden - Role '{user_role}' lacks access")
            return fn(user_context, *args, **kwargs)
        return wrapper
    return decorator

@require_roles(["ADMIN", "COACH"])
def update_player_health_data(user_context: dict, player_id: str, metric: dict):
    return {"status": "SUCCESS", "player_id": player_id, "updated_by": user_context.get("uid")}

if __name__ == "__main__":
    coach = {"uid": "u123", "role": "COACH"}
    print(update_player_health_data(coach, "p99", {"stamina": 92}))
