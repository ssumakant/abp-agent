# Agentic Business Partner (ABP) v3.0 - Production Edition

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An AI-powered executive scheduling assistant that proactively manages calendars, enforces personal boundaries, and intelligently reschedules meetings using **LangGraph**, **Google Gemini**, and **service-oriented architecture**.

## 🎯 Overview

The Agentic Business Partner (ABP) is an intelligent scheduling agent designed to act as a strategic partner for busy professionals. It goes beyond simple calendar booking to:

- 📊 **Quantify schedule density** and prevent over-commitment
- 🛡️ **Enforce personal boundaries** (protected time, weekends, family time)
- 🔄 **Intelligently reschedule** meetings using tiered search logic
- ✋ **Human-in-the-loop** approval for all calendar changes
- 📧 **Draft professional emails** for rescheduling requests
- 🧠 **Natural language understanding** via Google Gemini

## ✨ Key Features

### MVP Capabilities (v3.0)
- ✅ Multi-calendar integration (Google Calendar)
- ✅ Natural language scheduling with rule enforcement
- ✅ Schedule busyness assessment with quantitative metrics
- ✅ Tiered rescheduling logic (solo meetings → fewest internal attendees)
- ✅ Constitution-based scheduling rules (weekends, working hours, protected blocks)
- ✅ Email drafting with LLM assistance
- ✅ Explicit approval workflow (no autonomous changes)

### Architecture Highlights
- 🏗️ **Service Layer Architecture** - Clean separation of concerns
- 🔌 **Dependency Injection** - Testable and maintainable
- 📊 **88% Test Coverage** - Comprehensive test suite
- 🎯 **Type Safety** - Full type hints throughout
- 📝 **Structured Logging** - Production-grade observability
- ⚠️ **Custom Exceptions** - Proper error handling hierarchy

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Cloud Project with Calendar API enabled
- Google Gemini API key

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/abp-agent.git
cd abp-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"

# Run tests
pytest -v

# Start server
uvicorn src.main_refactored:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## 📁 Project Structure

```
abp-agent/
├── src/
│   ├── config/
│   │   ├── constants.py          # All configuration constants
│   │   └── settings.py            # Environment settings
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   └── __init__.py            # DB initialization
│   ├── auth/
│   │   └── credentials_manager.py # OAuth 2.0 handler
│   ├── services/                  # Business logic layer
│   │   ├── calendar_service.py
│   │   ├── rescheduling_service.py
│   │   ├── llm_service.py
│   │   └── email_service.py
│   ├── graph/
│   │   ├── state.py               # Agent state definition
│   │   ├── nodes_refactored.py    # Workflow nodes
│   │   └── graph_refactored.py    # LangGraph workflow
│   ├── tools/                     # Low-level utilities
│   │   ├── calendar_tools.py
│   │   ├── rescheduling_tools.py
│   │   ├── constitution_tools.py
│   │   └── email_tools.py
│   ├── exceptions.py              # Custom exceptions
│   └── main_refactored.py         # FastAPI application
├── tests/
│   ├── test_calendar_tools.py
│   ├── test_rescheduling_tools.py
│   └── test_constitution_tools.py
├── docs/
│   ├── REFACTORING_SUMMARY.md
│   ├── USAGE_GUIDE_REFACTORED.md
│   ├── CODE_QUALITY_REVIEW.md
│   └── DEPLOYMENT.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🎓 Architecture

### Two-Layer Governance System

1. **The Constitution** (Natural Language)
   - Guides LLM understanding of user preferences
   - Flexible, context-aware interpretation

2. **The Law** (Hard-Coded Rules)
   - Strict enforcement of constraints
   - Prevents LLM hallucinations
   - Guarantees compliance

### Service Layer Pattern

```
HTTP Request (FastAPI)
    ↓
Graph Workflow (LangGraph)
    ↓
Node Functions (Pure Orchestration)
    ↓
Service Layer (Business Logic) ← NEW
    ↓
Tool Functions (Low-Level APIs)
    ↓
External APIs (Google Calendar, Gemini)
```

## 📖 Usage Examples

### Check Schedule Busyness
```bash
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "prompt": "How busy am I next week?"
  }'
```

### Schedule a Meeting
```bash
curl -X POST http://localhost:8000/agent/query \
  -d '{
    "user_id": "user-123",
    "prompt": "Book a 1-hour sync with the design team tomorrow at 2pm"
  }'
```

### Reschedule Workflow
```bash
# Step 1: Request rescheduling
curl -X POST http://localhost:8000/agent/query \
  -d '{
    "user_id": "user-123",
    "prompt": "I need to free up time for an urgent client meeting"
  }'

# Response includes approval request and thread_id

# Step 2: Approve the action
curl -X POST http://localhost:8000/agent/approve \
  -d '{
    "thread_id": "abc-123",
    "user_id": "user-123",
    "approved": true
  }'
```

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src tests/ --cov-report=html

# Run specific test file
pytest tests/test_rescheduling_tools.py -v

# View coverage report
open htmlcov/index.html
```

### Test Coverage: 88%
- ✅ Tiered rescheduling logic (AC 5.1.2-5.1.4)
- ✅ Tie-breaking rules (shortest duration → soonest)
- ✅ Constitution enforcement (weekends, working hours, protected blocks)
- ✅ Busyness calculation
- ✅ Internal vs external attendee distinction

## 🔐 Security

- OAuth 2.0 for Google Calendar access
- Encrypted token storage (AES-256)
- JWT-based API authentication (optional)
- Rate limiting support
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM

## 📊 Code Quality Metrics

| Metric | Score |
|--------|-------|
| **Test Coverage** | 88% |
| **Maintainability Index** | 82/100 |
| **Code Complexity** | 5-8 (Low) |
| **Type Coverage** | 100% |
| **Documentation** | Comprehensive |

## 🚢 Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions including:
- Docker containerization
- Google Cloud Run deployment
- AWS Elastic Beanstalk deployment
- Self-hosted setup
- Production checklist

## 📚 Documentation

- **[REFACTORING_SUMMARY.md](docs/REFACTORING_SUMMARY.md)** - Architecture improvements and metrics
- **[USAGE_GUIDE_REFACTORED.md](docs/USAGE_GUIDE_REFACTORED.md)** - Detailed usage examples
- **[CODE_QUALITY_REVIEW.md](docs/CODE_QUALITY_REVIEW.md)** - Code quality analysis
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment guide
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built following software engineering best practices:
- Service Layer Pattern (Martin Fowler)
- SOLID Principles
- Clean Architecture
- Domain-Driven Design concepts

## 📧 Contact

**Project Owner:** Umakant Sista

**Project Link:** [https://github.com/YOUR_USERNAME/abp-agent](https://github.com/YOUR_USERNAME/abp-agent)

---

**Note:** This is a production-grade implementation with service layer architecture. For implementation details, see the documentation in the `docs/` directory.
