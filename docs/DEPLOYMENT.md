# Production Deployment Checklist

## ✅ Pre-Deployment

### 1. Environment Configuration
- [ ] Set strong `SECRET_KEY` (32+ characters)
- [ ] Configure production `DATABASE_URL` (PostgreSQL recommended)
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure proper CORS origins in `main.py`
- [ ] Set up proper redirect URIs in Google Cloud Console

### 2. Security
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Implement rate limiting on API endpoints
- [ ] Set up API key rotation schedule
- [ ] Configure firewall rules
- [ ] Enable database connection encryption
- [ ] Review and restrict OAuth scopes to minimum required

### 3. Database
- [ ] Migrate from SQLite to PostgreSQL
- [ ] Set up database backups (daily minimum)
- [ ] Configure connection pooling
- [ ] Create database indexes on frequently queried fields:
  ```sql
  CREATE INDEX idx_users_email ON users(email);
  CREATE INDEX idx_oauth_tokens_user_id ON oauth_tokens(user_id);
  ```

### 4. Secrets Management
- [ ] Move from `.env` to proper secrets manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault)
- [ ] Encrypt OAuth tokens at rest (implement AES-256)
- [ ] Set up key rotation for access tokens

### 5. Monitoring & Logging
- [ ] Set up application logging (structured JSON logs)
- [ ] Configure error tracking (Sentry, Rollbar, etc.)
- [ ] Set up uptime monitoring
- [ ] Create dashboards for key metrics:
  - API response times
  - Error rates
  - LLM token usage
  - Database query performance
- [ ] Set up alerts for critical errors

### 6. Testing
- [ ] Run full test suite: `pytest`
- [ ] Perform load testing
- [ ] Test OAuth flow end-to-end
- [ ] Verify all approval workflows
- [ ] Test with real calendar data

## 🚀 Deployment Steps

### Option A: Docker Deployment

1. **Create Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env .env

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Build and run**:
```bash
docker build -t abp-agent .
docker run -p 8000:8000 --env-file .env abp-agent
```

### Option B: Cloud Platform Deployment

#### Google Cloud Run
```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/abp-agent

# Deploy
gcloud run deploy abp-agent \
  --image gcr.io/PROJECT_ID/abp-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### AWS Elastic Beanstalk
```bash
# Initialize
eb init -p python-3.11 abp-agent

# Create environment
eb create abp-agent-prod

# Deploy
eb deploy
```

#### Azure App Service
```bash
# Create resource group
az group create --name abp-agent-rg --location eastus

# Create app service plan
az appservice plan create --name abp-plan --resource-group abp-agent-rg

# Deploy
az webapp up --name abp-agent --resource-group abp-agent-rg
```

## 🔧 Post-Deployment

### 1. Verification
- [ ] Health check endpoint responding: `curl https://your-domain.com/`
- [ ] Database connectivity working
- [ ] OAuth flow completing successfully
- [ ] Test end-to-end user journey
- [ ] Verify LLM API calls working
- [ ] Check calendar API integration

### 2. Performance Tuning
- [ ] Set appropriate worker count for uvicorn:
  ```bash
  uvicorn src.main:app --workers 4 --host 0.0.0.0 --port 8000
  ```
- [ ] Configure database connection pool size
- [ ] Enable response caching where appropriate
- [ ] Optimize LLM prompts for token efficiency

### 3. Documentation
- [ ] Update API documentation with production URL
- [ ] Document OAuth setup for end users
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedures

## 🔄 Ongoing Maintenance

### Daily
- [ ] Monitor error logs
- [ ] Check API response times
- [ ] Review LLM token usage

### Weekly
- [ ] Review and analyze user feedback
- [ ] Check database growth and performance
- [ ] Review security logs

### Monthly
- [ ] Rotate API keys
- [ ] Review and update dependencies: `pip list --outdated`
- [ ] Analyze cost and optimize if needed
- [ ] Review and test backup restoration

### Quarterly
- [ ] Security audit
- [ ] Performance review
- [ ] Capacity planning
- [ ] Update documentation

## 🚨 Emergency Procedures

### API is Down
1. Check health endpoint
2. Review application logs
3. Verify database connectivity
4. Check LLM API status
5. Restart service if needed

### Data Breach Response
1. Immediately rotate all API keys and secrets
2. Revoke affected OAuth tokens
3. Notify affected users
4. Review access logs
5. Patch vulnerability
6. Conduct post-mortem

### High Error Rate
1. Check LLM API status and quotas
2. Review recent deployments
3. Check database performance
4. Review error logs for patterns
5. Scale resources if needed

## 📊 Production Configuration Best Practices

### Environment Variables
```bash
# Production settings
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000

# Database (use managed service)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/abp_prod

# Security
SECRET_KEY=<generated-secret-key>
ALGORITHM=HS256

# APIs
GOOGLE_API_KEY=<from-secrets-manager>
GOOGLE_CLIENT_ID=<from-secrets-manager>
GOOGLE_CLIENT_SECRET=<from-secrets-manager>

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
LOG_LEVEL=INFO
```

### Uvicorn Production Config
```bash
uvicorn src.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --limit-concurrency 100 \
  --timeout-keep-alive 5 \
  --log-level info \
  --access-log
```

## 🔐 Security Hardening

### API Security
```python
# Add to src/main.py

from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# JWT authentication
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token for protected endpoints."""
    token = credentials.credentials
    # Implement JWT verification
    # Raise HTTPException if invalid
    return user_id

# Apply to endpoints
@app.post("/agent/query")
@limiter.limit("10/minute")
async def agent_query(
    request: AgentRequest,
    user_id: str = Depends(verify_token)
):
    # ... endpoint logic
```

### HTTPS Enforcement
```python
# Add middleware to redirect HTTP to HTTPS
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### Input Validation
- All user inputs validated with Pydantic models ✓
- SQL injection prevented via SQLAlchemy ORM ✓
- XSS prevention via proper response encoding ✓

### OAuth Token Encryption
```python
# Implement in credentials_manager.py
from cryptography.fernet import Fernet

class CredentialsManager:
    def __init__(self, session, encryption_key):
        self.cipher = Fernet(encryption_key)
    
    async def save_credentials(self, user_id, creds):
        # Encrypt before storing
        encrypted_token = self.cipher.encrypt(creds.token.encode())
        # Store encrypted_token in database
```

## 📈 Scaling Considerations

### Horizontal Scaling
- FastAPI is stateless (except for LangGraph checkpointer)
- Use external checkpointer (Redis, PostgreSQL) for multi-instance deployments
- Load balancer configuration:
  ```nginx
  upstream abp_backend {
      server app1:8000;
      server app2:8000;
      server app3:8000;
  }
  ```

### Caching Strategy
```python
# Add Redis caching for frequently accessed data
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="abp-cache")

# Cache user context
@cache(expire=300)  # 5 minutes
async def get_user_context(user_id: str):
    # ...
```

### Database Optimization
- Connection pooling:
  ```python
  engine = create_async_engine(
      DATABASE_URL,
      pool_size=20,
      max_overflow=10,
      pool_pre_ping=True
  )
  ```
- Read replicas for query-heavy operations
- Partitioning for oauth_tokens table by user_id

## 💰 Cost Optimization

### LLM API Usage
- Implement prompt caching
- Use cheaper models for simple intent detection
- Batch multiple tool calls where possible
- Monitor token usage per user

### Database
- Archive old conversation threads
- Implement data retention policies
- Use appropriate instance sizes

### Infrastructure
- Auto-scaling based on load
- Scheduled scaling for known peak times
- Use spot instances for non-critical workloads

## 🧪 Continuous Integration/Deployment

### GitHub Actions Example
```yaml
name: Deploy ABP Agent

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src tests/
      - name: Check coverage
        run: coverage report --fail-under=80

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Your deployment commands here
          gcloud run deploy abp-agent --image gcr.io/$PROJECT_ID/abp-agent
```

## 📋 Compliance & Privacy

### GDPR Compliance
- [ ] Implement user data export endpoint
- [ ] Implement user data deletion endpoint
- [ ] Add consent tracking for data usage
- [ ] Document data retention policies
- [ ] Create privacy policy

### Data Handling
- [ ] Encrypt all PII at rest
- [ ] Minimize data collection
- [ ] Implement audit logging for data access
- [ ] Regular security assessments

## 🎯 Success Metrics

### Technical Metrics
- API response time: p95 < 3 seconds (per PRD NFR)
- Uptime: 99.8% during business hours (per PRD NFR)
- Error rate: < 0.5%
- LLM accuracy: > 95% intent detection

### Business Metrics
- User adoption rate
- Time saved per user (target: 40% reduction per BRD)
- Protected time adherence: 100% (per BRD)
- User satisfaction score

## 🔍 Troubleshooting Guide

### Common Production Issues

**Issue**: High latency on /agent/query
- **Diagnosis**: Check LLM API response times, database query performance
- **Fix**: Implement caching, optimize prompts, scale infrastructure

**Issue**: OAuth tokens expiring
- **Diagnosis**: Check token refresh logic in credentials_manager
- **Fix**: Ensure refresh_token is being used correctly, check token expiry handling

**Issue**: Calendar API rate limits
- **Diagnosis**: Review API quota usage in Google Cloud Console
- **Fix**: Implement request batching, add exponential backoff, request quota increase

**Issue**: Database connection pool exhausted
- **Diagnosis**: Check active connections, slow queries
- **Fix**: Increase pool size, optimize queries, add connection timeout

## 📞 Support & Maintenance

### Monitoring Dashboards
Create dashboards for:
1. **API Health**: Request rate, error rate, latency
2. **LLM Performance**: Token usage, cost, response time
3. **Database**: Query performance, connection pool usage
4. **Business Metrics**: Active users, approvals given, meetings rescheduled

### Alert Thresholds
- Error rate > 1% for 5 minutes
- API latency p95 > 5 seconds
- Database connection pool > 80% utilization
- LLM API error rate > 5%

### On-Call Procedures
1. Check alert details
2. Review application logs
3. Check external service status (Google APIs, LLM)
4. Follow runbook for specific issue
5. Escalate if needed
6. Document incident for post-mortem

---

## ✅ Final Checklist Before Go-Live

- [ ] All tests passing
- [ ] Security review completed
- [ ] Performance testing completed
- [ ] Backup procedures tested
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team trained
- [ ] Rollback plan in place
- [ ] Support procedures documented
- [ ] Legal/compliance review completed

---

**Remember**: Start with a limited beta rollout, gather feedback, iterate, then scale to full production.