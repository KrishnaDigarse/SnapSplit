# Monitoring & Observability

## Logging
We use structured logging via `RequestLoggingMiddleware` in `app/core/middleware.py`.

### Log Format
```
Request: {
  "method": "GET",
  "path": "/api/v1/groups",
  "status_code": 200,
  "duration": "0.0150s",
  "client": "127.0.0.1"
}
```

## Metrics to Watch
1.  **Request Duration**: High duration indicates API bottlenecks.
2.  **Error Rate (5xx)**: Application crashes.
3.  **Celery Queue Depth**: Backlog in AI processing on RabbitMQ/Redis.

## Future Improvements
- Integrate **Prometheus** for metric scraping.
- Use **Grafana** for dashboards.
- Set up **Sentry** for error tracking.
