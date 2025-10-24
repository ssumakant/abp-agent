# Agentic Business Partner (ABP) v3.0.1

AI-powered executive scheduling assistant with LangGraph and Google Gemini.

## Recent Updates (v3.0.1)

✅ **Fixed** - NoneType errors in intent detection
✅ **Fixed** - Message duplication in responses
✅ **Fixed** - Silent calendar API errors
✅ **Enhanced** - Better error messages and fallback handling
✅ **Added** - Complete CalendarService implementation

See [CHANGELOG.md](CHANGELOG.md) for detailed changes.

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
