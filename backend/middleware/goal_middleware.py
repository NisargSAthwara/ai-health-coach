from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class GoalContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Placeholder for goal context logic
        # This is where you would retrieve goal information (e.g., from session, headers, or DB)
        # and attach it to the request state.
        request.state.goal_id = None # Example: default to None
        request.state.goal_details = {} # Example: default to empty dict

        response = await call_next(request)
        return response