"""API module for Alter-5 Origination Engine.

Contains FastAPI endpoints for webhooks and external integrations.
"""

from api.webhooks import app

__all__ = ["app"]
