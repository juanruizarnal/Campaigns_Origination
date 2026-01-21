"""Orchestration module for Alter-5 Origination Engine.

Contains Celery tasks, schedulers, and event bus for the 24/7 autonomous system.
"""

from orchestration.tasks import celery_app

__all__ = ["celery_app"]
