# Gradio Implementation Guide
## Fork 1: Quick & Dirty Prototype

**File**: `gradio_app.py`
**Purpose**: Rapid internal testing and backend validation
**Status**: Complete & Functional

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Code Structure](#3-code-structure)
4. [Features Implemented](#4-features-implemented)
5. [UI Components](#5-ui-components)
6. [State Management](#6-state-management)
7. [API Integration](#7-api-integration)
8. [Styling & Customization](#8-styling--customization)
9. [Limitations](#9-limitations)
10. [Usage Examples](#10-usage-examples)

---

## 1. Overview

### Purpose
The Gradio prototype provides a **functional UI for testing the backend** without requiring complex frontend tooling. It's designed for:
- Internal testing of agent logic
- Backend API validation
- Quick demonstrations
- Debugging workflows

### Technology
- **Gradio 4.x**: Python-based UI framework
- **Requests 2.x**: HTTP library for API calls
- **Python 3.9+**: Runtime environment

### Key Characteristics
- ✅ Single file (self-contained)
- ✅ Zero build step
- ✅ 5-minute setup
- ✅ Python-native
- ⚠️ Not production-ready
- ⚠️ Limited customization

---

## 2. Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────┐
│            Gradio Application                   │
│  ┌───────────────────────────────────────────┐  │
│  │        User Interface (gr.Blocks)         │  │
│  │  ┌─────────────┐  ┌──────────────────┐   │  │
│  │  │  Auth Tabs  │  │  Chat Interface   │   │  │
│  │  │  • Login    │  │  • Chatbot        │   │  │
│  │  │  • Sign Up  │  │  • Input          │   │  │
│  │  └─────────────┘  │  • Approval Cards │   │  │
│  │                   └──────────────────────┘   │  │
│  └───────────────────────────────────────────┘  │
│                      ↕                          │
│  ┌───────────────────────────────────────────┐  │
│  │        State (gr.State)                   │  │
│  │  • jwt_token                              │  │
│  │  • thread_id                              │  │
│  │  • approval_state                         │  │
│  └───────────────────────────────────────────┘  │
│                      ↕                          │
│  ┌───────────────────────────────────────────┐  │
│  │     Python Functions (Business Logic)     │  │
│  │  • signup_user()                          │  │
│  │  • login_user()                           │  │
│  │  • send_agent_query()                     │  │
│  │  • handle_approval()                      │  │
│  │  • connect_google_calendar()              │  │
│  └───────────────────────────────────────────┘  │
│                      ↕                          │
│  ┌───────────────────────────────────────────┐  │
│  │     API Integration (requests)            │  │
│  │  • make_request()                         │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                       ↕
                  HTTP/HTTPS
                       ↕
┌─────────────────────────────────────────────────┐
│            Backend API (FastAPI)                │
│          http://localhost:8000                  │
└─────────────────────────────────────────────────┘
```

---

## 3. Code Structure

### File Organization

```python
# gradio_app.py

# 1. IMPORTS & CONFIGURATION
import gradio as gr
import requests
import json
from typing import Optional, Dict, Any, List, Tuple
import os
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
CUSTOM_CSS = """..."""

# 2. HELPER FUNCTIONS
def make_request(method, endpoint, token=None, data=None) -> Dict:
    """Generic HTTP request wrapper"""

# 3. AUTHENTICATION FUNCTIONS
def signup_user(email, password, internal_domain, timezone):
    """Create new user account"""

def login_user(email, password):
    """Authenticate and get JWT token"""

# 4. AGENT INTERACTION FUNCTIONS
def send_agent_query(message, token, chat_history, thread_id=None):
    """Send message to agent"""

def format_approval_card(approval_type, approval_data, context):
    """Format HTML for approval cards"""

def handle_approval(approve, token, approval_state, chat_history):
    """Process user approval/denial"""

# 5. UTILITY FUNCTIONS
def connect_google_calendar(token):
    """Initiate OAuth flow"""

def logout_user():
    """Clear session"""

# 6. GRADIO INTERFACE DEFINITION
with gr.Blocks(css=CUSTOM_CSS, title="Agentic ABP") as app:
    # State variables
    jwt_token = gr.State(None)
    is_authenticated = gr.State(False)
    thread_id = gr.State(None)
    approval_state = gr.State({})

    # UI Components
    # - Auth Section (Login/Signup tabs)
    # - Chat Section
    # - Approval UI

    # Event Handlers
    # - Login button click
    # - Signup button click
    # - Message send
    # - Approval buttons
    # - Calendar connection
    # - Logout

# 7. LAUNCH CONFIGURATION
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
```

### Code Metrics
- **Total Lines**: ~500
- **Functions**: 10
- **UI Components**: 15+
- **Event Handlers**: 8

---

## 4. Features Implemented

### ✅ Authentication

**Sign Up**:
```python
def signup_user(email, password, internal_domain, timezone):
    result = make_request(
        "POST",
        "/users",
        data={
            "email": email,
            "password": password,
            "internal_domain": internal_domain,
            "timezone": timezone or "America/Los_Angeles"
        }
    )

    if result["success"]:
        return "✅ Account created! Please login."
    else:
        return f"❌ Error: {result['error']}"
```

**Login**:
```python
def login_user(email, password):
    # OAuth2 form data format
    response = requests.post(
        f"{API_BASE_URL}/token",
        data={"username": email, "password": password}
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        return (
            "✅ Welcome!",
            True,  # is_authenticated
            token,
            gr.update(visible=True)  # Show chat
        )
```

**State Management**:
- JWT token stored in `gr.State(None)`
- Token passed to all authenticated requests
- Cleared on logout

### ✅ Conversational Interface

**Chat History**:
```python
chatbot = gr.Chatbot(
    label="Conversation",
    height=400,
    show_copy_button=True
)
```

**Message Sending**:
```python
def send_agent_query(message, token, chat_history, thread_id):
    # Add user message (optimistic update)
    chat_history.append((message, "🤔 Thinking..."))

    # Call backend
    result = make_request(
        "POST",
        "/agent/invoke",
        token=token,
        data={"query": message, "user_id": thread_id}
    )

    # Update with real response
    agent_response = result["data"]["response"]
    chat_history[-1] = (message, agent_response)

    # Check for approval needed
    if result["data"]["requires_approval"]:
        show_approval_card()

    return chat_history
```

### ✅ Approval Flow

**Approval Card HTML**:
```python
def format_approval_card(approval_type, approval_data, context):
    if approval_type == "constitution_override":
        card_class = "approval-card approval-card-override"
        title = "⚠️ Override Required"
    elif approval_type == "reschedule_meeting":
        card_class = "approval-card"
        title = "📅 Approval Needed"

    html = f"""
    <div class="{card_class}">
        <h3>{title}</h3>
        <p>{context}</p>
        <!-- Display approval_data -->
    </div>
    """
    return html
```

**Approval Handling**:
```python
def handle_approval(approve, token, approval_state, chat_history):
    result = make_request(
        "POST",
        "/agent/approve",
        token=token,
        data={
            "thread_id": approval_state["thread_id"],
            "approved": approve,
            "user_id": approval_state["thread_id"]
        }
    )

    response_text = result["data"]["response"]
    chat_history.append(
        (f"[User {'approved' if approve else 'denied'}]", response_text)
    )

    return chat_history
```

### ✅ Calendar Connection

```python
def connect_google_calendar(token):
    # Mock implementation (endpoint not yet available)
    return """
    📋 Google Calendar Connection:

    This feature requires backend endpoint:
    GET /api/v1/auth/google/url

    See BACKEND_CHANGE_REQUEST.md for details.
    """
```

---

## 5. UI Components

### Component Inventory

| Component | Type | Purpose |
|-----------|------|---------|
| `auth_tabs` | `gr.Tabs` | Login/Signup switcher |
| `login_email` | `gr.Textbox` | Email input (login) |
| `login_password` | `gr.Textbox` | Password input (login) |
| `login_btn` | `gr.Button` | Submit login |
| `signup_email` | `gr.Textbox` | Email input (signup) |
| `signup_password` | `gr.Textbox` | Password input (signup) |
| `signup_domain` | `gr.Textbox` | Internal domain input |
| `signup_timezone` | `gr.Textbox` | Timezone input |
| `signup_btn` | `gr.Button` | Submit signup |
| `chatbot` | `gr.Chatbot` | Conversation history |
| `approval_card` | `gr.HTML` | Approval request display |
| `approval_buttons_row` | `gr.Row` | Approve/Deny buttons |
| `msg_input` | `gr.Textbox` | Message input |
| `send_btn` | `gr.Button` | Send message |
| `calendar_btn` | `gr.Button` | Connect calendar |
| `logout_btn` | `gr.Button` | Logout |

### Layout Structure

```python
with gr.Blocks() as app:
    # Header
    gr.Markdown("# Agentic ABP")

    # Auth Section (visible when not authenticated)
    with gr.Column(visible=True) as auth_section:
        with gr.Tabs():
            with gr.Tab("Login"):
                # Login form
            with gr.Tab("Sign Up"):
                # Signup form

    # Chat Section (hidden until authenticated)
    with gr.Column(visible=False) as chat_section:
        chatbot = gr.Chatbot()
        approval_card = gr.HTML(visible=False)

        with gr.Row(visible=False) as approval_buttons_row:
            approve_btn = gr.Button("✅ Confirm")
            deny_btn = gr.Button("❌ Deny")

        with gr.Row():
            msg_input = gr.Textbox()
            send_btn = gr.Button("Send")

        with gr.Row():
            calendar_btn = gr.Button("Connect Calendar")
            logout_btn = gr.Button("Logout")
```

---

## 6. State Management

### State Variables

```python
# Global application state (gr.State)
jwt_token = gr.State(None)            # JWT authentication token
is_authenticated = gr.State(False)     # Login status
thread_id = gr.State(None)            # Current conversation thread
approval_state = gr.State({})         # Pending approval data
```

### State Updates

**Login Flow**:
```python
# Initial state
jwt_token = None
is_authenticated = False

# After login
jwt_token = "eyJhbGc..."
is_authenticated = True
chat_section visible = True
auth_section visible = False
```

**Approval Flow**:
```python
# Approval needed
approval_state = {
    "thread_id": "uuid",
    "approval_type": "constitution_override",
    "approval_data": {...}
}
approval_card visible = True
approval_buttons_row visible = True

# After approval
approval_state = {}
approval_card visible = False
approval_buttons_row visible = False
```

### State Persistence

⚠️ **Limitation**: State is **lost on page refresh**
- JWT token stored in memory only
- No localStorage/cookies
- Refresh = re-login required

---

## 7. API Integration

### Request Function

```python
def make_request(method: str, endpoint: str, token: Optional[str] = None,
                 data: Optional[Dict] = None) -> Dict:
    """
    Generic HTTP request wrapper

    Args:
        method: HTTP method (GET, POST, DELETE)
        endpoint: API endpoint path
        token: Optional JWT token
        data: Optional request body (JSON)

    Returns:
        {"success": bool, "data": dict} or {"success": bool, "error": str}
    """
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)

        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to backend"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### API Endpoints Used

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/users` | POST | Create account | No |
| `/token` | POST | Login (OAuth2 form) | No |
| `/agent/invoke` | POST | Send agent query | Yes |
| `/agent/approve` | POST | Approval response | Yes |

### Error Handling

**Network Errors**:
```python
try:
    response = requests.post(...)
except requests.exceptions.ConnectionError:
    return "❌ Cannot connect to backend at {API_BASE_URL}"
except requests.exceptions.Timeout:
    return "❌ Request timed out. Is the backend running?"
```

**API Errors**:
```python
if response.status_code == 401:
    return "❌ Login failed: Invalid credentials"
elif response.status_code == 400:
    return f"❌ Error: {response.text}"
```

---

## 8. Styling & Customization

### Custom CSS

```python
CUSTOM_CSS = """
.gradio-container {
    font-family: 'Inter', sans-serif;
}

.approval-card {
    background: #FEF3C7;
    border: 2px solid #F59E0B;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
}

.approval-card-override {
    background: #FEE2E2;
    border: 2px solid #DC2626;
}

.success-message {
    background: #D1FAE5;
    border: 2px solid #10B981;
    border-radius: 8px;
    padding: 12px;
}

.error-message {
    background: #FEE2E2;
    border: 2px solid #DC2626;
    border-radius: 8px;
    padding: 12px;
}
"""
```

### Component Styling

Gradio's built-in styling options:

```python
gr.Button(
    "Login",
    variant="primary",  # Blue button
    size="large"
)

gr.Textbox(
    label="Email",
    placeholder="user@company.com",
    type="email"
)

gr.Chatbot(
    height=400,
    show_copy_button=True,
    bubble_full_width=False
)
```

---

## 9. Limitations

### Technical Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| **No Modal Dialogs** | Email review shown inline | Use `gr.HTML` for card display |
| **Limited Styling** | Cannot match wireframes exactly | Custom CSS for basic branding |
| **Simple State** | No persistent sessions | Store critical data in `gr.State` |
| **Single Thread** | No conversation history | Use backend thread management |
| **No File Upload** | Cannot attach files | Not needed for MVP |
| **Refresh Clears State** | User must re-login | Document this behavior |

### Feature Gaps vs React

| Feature | Gradio | React |
|---------|--------|-------|
| Settings Page | ❌ Not implemented | ✅ Full implementation |
| Account Management | ❌ Mock only | ✅ Full implementation |
| Email Editing | ❌ Inline display | ✅ Modal with editing |
| Multi-threading | ❌ Single thread | ✅ Multiple threads |
| URL Routing | ❌ Single page | ✅ React Router |
| Offline Support | ❌ No | ✅ Possible (PWA) |

### When to Use Gradio

✅ **Good For**:
- Quick backend testing
- Internal demos
- Debugging agent logic
- Proof of concept

❌ **Not Good For**:
- Production deployment
- Investor presentations
- Complex UX flows
- Custom branding

---

## 10. Usage Examples

### Example 1: Sign Up Flow

```
1. User opens http://localhost:7860
2. Clicks "Sign Up" tab
3. Enters:
   - Email: test@company.com
   - Password: secure_password
   - Domain: company.com
   - Timezone: America/Los_Angeles
4. Clicks "Create Account"
5. Sees: "✅ Account created! Please login."
6. Switches to "Login" tab
```

### Example 2: Chat Flow

```
1. User logs in
2. Chat interface appears
3. Types: "Am I free tomorrow at 2pm?"
4. Clicks "Send"
5. Sees:
   User: Am I free tomorrow at 2pm?
   Agent: 🤔 Thinking...
6. Agent responds:
   Agent: Checking your calendar... Yes, you are free tomorrow at 2pm.
```

### Example 3: Approval Flow

```
1. User types: "Book a meeting this Saturday"
2. Agent responds with approval card:

   ┌─────────────────────────────────────────┐
   │ ⚠️ Override Required                    │
   │                                         │
   │ The requested action violates your rule:│
   │ "No business meetings on weekends"     │
   │                                         │
   │ [✅ Confirm]  [❌ Deny]                  │
   └─────────────────────────────────────────┘

3. User clicks "✅ Confirm"
4. Agent: "Meeting scheduled for Saturday."
```

---

## Appendix: Complete Code Walkthrough

### Initialization

```python
import gradio as gr
import requests
import json
from typing import Optional, Dict, Any, List, Tuple
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
```

### Main Application Block

```python
with gr.Blocks(css=CUSTOM_CSS, title="Agentic ABP") as app:
    # State
    jwt_token = gr.State(None)
    is_authenticated = gr.State(False)
    thread_id = gr.State(None)
    approval_state = gr.State({})

    # Header
    gr.Markdown("# 🤖 Agentic ABP")

    # Auth Section
    with gr.Column(visible=True) as auth_section:
        # Login/Signup tabs
        pass

    # Chat Section
    with gr.Column(visible=False) as chat_section:
        # Chatbot, input, buttons
        pass

    # Event Handlers
    login_btn.click(
        fn=login_user,
        inputs=[login_email, login_password],
        outputs=[login_status, is_authenticated, jwt_token, chat_section]
    ).then(
        fn=lambda: gr.update(visible=False),
        outputs=auth_section
    )
```

### Launch

```python
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )
```

---

**Status**: Complete & Functional
**Maintenance**: Bug fixes only
**Recommended Use**: Internal testing
**Not Recommended**: Production deployment
