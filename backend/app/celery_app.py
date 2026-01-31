"""
Celery application instance for SnapSplit.

This module initializes the Celery app and configures it for async task processing.
Tasks are auto-discovered from the app.tasks module.

Usage:
    # Start worker
    celery -A app.celery_app worker --loglevel=info
    
    # Start worker with concurrency
    celery -A app.celery_app worker --loglevel=info --concurrency=4
"""
import os
from celery import Celery
from app.core import celery_config

# Create Celery app
celery_app = Celery("snapsplit")

# Load configuration from celery_config module
celery_app.config_from_object(celery_config)

# Auto-discover tasks from app.tasks module
celery_app.autodiscover_tasks(["app.tasks"])

# Explicitly import tasks to ensure registration
from app.tasks import ai_tasks  # noqa: F401


# Optional: Configure logging
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Configure periodic tasks here if needed in the future.
    Currently not used, but kept for future enhancements.
    """
    pass

if __name__ == "__main__":
    celery_app.start()
