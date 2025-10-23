# Agentic Business Partner (ABP) v3.0

AI-powered executive scheduling assistant with LangGraph and Google Gemini.

## Features

- 📊 Schedule density analysis
- 🛡️ Personal time protection
- 🔄 Intelligent rescheduling
- ✋ Human-in-the-loop approval
- 📧 Email drafting
- 🧠 Natural language understanding

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

## Documentation

- [Setup Guide](docs/USAGE_GUIDE_REFACTORED.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Architecture](docs/REFACTORING_SUMMARY.md)

## Testing

```bash
pytest -v
```

## License

MIT License - see LICENSE file for details.
