"""
This module sets up the API routing for a FastAPI application. It includes routes for conversation, documents, and health endpoints. Each route is associated with its respective endpoint in the 'api.endpoints' package. The module defines the base path and tags for each route, allowing for organized and accessible API documentation and interaction.
"""
from fastapi import APIRouter

from api.endpoints import conversation, documents, health

api_router = APIRouter()
api_router.include_router(
    conversation.router, prefix="/conversation", tags=["conversation"]
)
api_router.include_router(
    documents.router, prefix="/document", tags=["document"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
