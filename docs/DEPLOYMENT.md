# MARLIN Backend Deployment Guide

## Production Optimizations

### Playwright Image Size Optimization

The current Docker image includes the full Playwright installation (~150MB for Chromium). For production deployment, especially on Fly.io, consider optimizing:

```dockerfile
# In production Dockerfile, replace the current playwright installation with:
RUN pip install playwright>=1.40 && \
    playwright install --with-deps chromium --browser chromium
```

This installs only Chromium browser instead of all browsers, reducing image size significantly.

### Database Migration Strategy

The current setup uses SQLAlchemy metadata-based table creation for simplicity. For production:

1. **Development**: Use the current `scripts/init-db.py` approach
2. **Production**: Consider switching back to Alembic for proper migration management
3. **CI/CD**: Run `alembic upgrade head` in deployment pipelines

### Environment Configuration

Ensure the following environment variables are set:

```bash
POSTGRES_HOST=your-production-db-host
POSTGRES_PORT=5432
POSTGRES_DB=marlin
POSTGRES_USER=marlin
POSTGRES_PASSWORD=secure-password
APP_ENV=production
APP_DEBUG=false
```

### Scheduling Considerations

The current scheduler runs 28 jobs (7 stations × 4 time windows). In production:

1. Monitor scheduler performance and memory usage
2. Consider using external cron jobs for very high-scale deployments
3. Implement proper logging for scheduled job execution

### Security

1. Use secure database passwords
2. Enable SSL for database connections in production
3. Configure proper CORS settings for API access
4. Consider API rate limiting for public endpoints 