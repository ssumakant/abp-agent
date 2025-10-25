# Agentic Business Partner (ABP) v3.1.0

AI-powered executive scheduling assistant with LangGraph and Google Gemini.

## 🔥 Latest Updates (v3.1.0 - October 25, 2025)

### Critical Bug Fixes
🐛 **Fixed** - NameError crash in `/agent/query` and `/agent/approve` endpoints
🐛 **Fixed** - Stateful/stateless conflict breaking Human-in-the-Loop workflows
✅ **Implemented** - Persistent checkpointing with AsyncSqliteSaver

### New Features
✨ **Added** - 5 new API endpoints for Settings & Account Management
✨ **Added** - GET/POST `/api/v1/settings` for constitution management
✨ **Added** - Google account management endpoints (list, connect, remove)
✨ **Enhanced** - Database schema with account status tracking

See [CHANGELOG.md](CHANGELOG.md) for detailed changes.
See [v3.1.0 Release Notes](docs/v3.1.0_RELEASE_NOTES.md) for complete documentation.

## Features

- 📊 Schedule density analysis
- 🛡️ Personal time protection
- 🔄 Intelligent rescheduling
- ✋ Human-in-the-loop approval
- 📧 Email drafting
- 🧠 Natural language understanding
- 🔐 JWT authentication with OAuth2

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
uvicorn src.main_refactored:app --reload
```

Visit http://localhost:8000/docs for API documentation.

## API Endpoints

### Agent Interaction
- `POST /agent/query` - Main agent interaction (stateful, supports approval workflows)
- `POST /agent/approve` - Approve/deny proposed actions
- `POST /agent/invoke` - Simple queries (stateless, requires JWT)

### Settings & Constitution
- `GET /api/v1/settings` - Get user's scheduling rules (JWT required)
- `POST /api/v1/settings` - Update scheduling preferences (JWT required)

### Account Management
- `GET /api/v1/auth/google/url` - Get OAuth URL for calendar connection (JWT required)
- `GET /api/v1/auth/accounts` - List connected Google Calendar accounts (JWT required)
- `DELETE /api/v1/auth/accounts/{id}` - Remove connected account (JWT required)

### Authentication
- `POST /users` - Create new user account
- `POST /token` - Login and get JWT access token
- `GET /auth/callback` - OAuth callback handler

See [v3.1.0 Release Notes](docs/v3.1.0_RELEASE_NOTES.md#new-api-endpoints) for detailed endpoint documentation with request/response examples.

## Project Structure

```
src/
├── main_refactored.py      # FastAPI app with JWT auth
├── schemas.py              # Pydantic models for API requests/responses
├── config.py               # Configuration and settings
├── exceptions.py           # Custom exception classes
├── database/               # SQLAlchemy models and session management
├── services/               # Business logic layer
│   ├── calendar_service.py
│   ├── llm_service.py
│   ├── rescheduling_service.py
│   └── email_service.py
├── graph/                  # LangGraph workflow
│   ├── nodes_refactored.py # Workflow node functions
│   ├── graph_refactored.py # Graph definition
│   └── state.py           # State type definitions
├── tools/                  # Low-level utility functions
├── auth/                   # OAuth and credentials management
└── configuration/          # Constants and intent definitions
```

## Documentation

- [Changelog](CHANGELOG.md) - Recent fixes and improvements
- [Setup Guide](docs/USAGE_GUIDE_REFACTORED.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Architecture](docs/ARCHITECTURE.md)

## Testing

```bash
pytest -v
```

## License

MIT License - see LICENSE file for details.
