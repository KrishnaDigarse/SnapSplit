"""
Celery configuration for SnapSplit.

This module contains all Celery-related settings including:
- Broker and backend configuration
- Task serialization
- Retry policies
- Timezone settings
"""
import os
from kombu import Exchange, Queue

# Broker settings
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Serialization
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# Timezone
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Task execution
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 600  # 10 minutes max per task
CELERY_TASK_SOFT_TIME_LIMIT = 540  # 9 minutes soft limit

# Result backend settings
CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour
CELERY_RESULT_PERSISTENT = True

# Task routing
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_DEFAULT_EXCHANGE = "default"
CELERY_TASK_DEFAULT_ROUTING_KEY = "default"

# Retry policy defaults
CELERY_TASK_AUTORETRY_FOR = (Exception,)
CELERY_TASK_RETRY_BACKOFF = True
CELERY_TASK_RETRY_BACKOFF_MAX = 600  # Max 10 minutes between retries
CELERY_TASK_RETRY_JITTER = True  # Add randomness to prevent thundering herd

# Worker settings
CELERYD_PREFETCH_MULTIPLIER = 1  # Only fetch one task at a time
CELERYD_MAX_TASKS_PER_CHILD = 100  # Restart worker after 100 tasks (prevent memory leaks)

# Logging
CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
