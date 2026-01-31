"""
Celery tasks package.

This package contains all background tasks for SnapSplit.
Tasks are auto-discovered by Celery.
"""
from app.tasks.ai_tasks import process_bill_image_task

__all__ = ["process_bill_image_task"]
