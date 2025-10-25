"""
Gradio Prototype for Agentic Administrative Business Partner (ABP)
Version: 1.0
Date: October 24, 2025

This is a "quick and dirty" functional prototype for internal testing.
It connects to the existing FastAPI backend.
"""

import gradio as gr
import requests
import json
from typing import Optional, Dict, Any, List, Tuple
import os
from datetime import datetime

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS for branding and improved UI
CUSTOM_CSS = """
.gradio-container {
    font-family: 'Inter', sans-serif;
}
.auth-container {
    max-width: 400px;
    margin: 0 auto;
}
.chat-container {
    max-width: 800px;
    margin: 0 auto;
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
    margin: 8px 0;
}
.error-message {
    background: #FEE2E2;
    border: 2px solid #DC2626;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}
"""

# Helper functions for API calls
def make_request(method: str, endpoint: str, token: Optional[str] = None, data: Optional[Dict] = None) -> Dict:
    """Make HTTP request to the backend API."""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}

        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Is the backend running?"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": f"Cannot connect to backend at {API_BASE_URL}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def signup_user(email: str, password: str, internal_domain: str, timezone: str) -> Tuple[str, bool, Optional[str], str]:
    """Sign up a new user."""
    if not email or not password or not internal_domain:
        return "❌ Please fill in all required fields.", False, None, gr.update(visible=False)

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
        return (
            f"✅ Account created successfully! Please login with {email}",
            False,
            None,
            gr.update(visible=False)
        )
    else:
        return f"❌ Signup failed: {result['error']}", False, None, gr.update(visible=False)


def login_user(email: str, password: str) -> Tuple[str, bool, Optional[str], str]:
    """Login and get JWT token."""
    if not email or not password:
        return "❌ Please enter email and password.", False, None, gr.update(visible=False)

    # FastAPI OAuth2PasswordRequestForm expects form data, not JSON
    url = f"{API_BASE_URL}/token"
    try:
        response = requests.post(
            url,
            data={"username": email, "password": password},  # Form data
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            return (
                f"✅ Welcome back, {email}!",
                True,
                token,
                gr.update(visible=True)
            )
        else:
            return f"❌ Login failed: {response.text}", False, None, gr.update(visible=False)

    except Exception as e:
        return f"❌ Login error: {str(e)}", False, None, gr.update(visible=False)


def send_agent_query(message: str, token: str, chat_history: List, thread_id: Optional[str] = None) -> Tuple[List, str, Optional[str], str, Dict]:
    """Send a query to the agent and handle the response."""
    if not message.strip():
        return chat_history, "", thread_id, gr.update(visible=False), {}

    if not token:
        chat_history.append((message, "❌ You must be logged in to use the agent."))
        return chat_history, "", thread_id, gr.update(visible=False), {}

    # Add user message to chat
    chat_history.append((message, "🤔 Thinking..."))

    # Send to backend
    result = make_request(
        "POST",
        "/agent/invoke",
        token=token,
        data={"query": message, "user_id": thread_id}
    )

    if not result["success"]:
        chat_history[-1] = (message, f"❌ Error: {result['error']}")
        return chat_history, "", thread_id, gr.update(visible=False), {}

    response_data = result["data"]
    agent_response = response_data.get("response", "No response from agent.")
    new_thread_id = response_data.get("thread_id", thread_id)
    requires_approval = response_data.get("requires_approval", False)
    approval_type = response_data.get("approval_type")
    approval_data = response_data.get("approval_data", {})

    # Update the last message with the actual response
    chat_history[-1] = (message, agent_response)

    # If approval is required, show approval card
    if requires_approval:
        approval_card_html = format_approval_card(approval_type, approval_data, agent_response)
        return (
            chat_history,
            "",
            new_thread_id,
            gr.update(visible=True, value=approval_card_html),
            {"thread_id": new_thread_id, "approval_type": approval_type, "approval_data": approval_data}
        )

    return chat_history, "", new_thread_id, gr.update(visible=False), {}


def format_approval_card(approval_type: str, approval_data: Dict, context: str) -> str:
    """Format the approval request as HTML."""
    if approval_type == "constitution_override":
        card_class = "approval-card approval-card-override"
        title = "⚠️ Override Required"
    elif approval_type == "reschedule_meeting":
        card_class = "approval-card"
        title = "📅 Approval Needed: Reschedule Meeting"
    else:
        card_class = "approval-card"
        title = "❓ Approval Needed"

    html = f"""
    <div class="{card_class}">
        <h3>{title}</h3>
        <p><strong>Context:</strong> {context}</p>
    """

    if approval_data:
        html += "<div style='margin-top: 12px; font-size: 0.9em;'>"
        for key, value in approval_data.items():
            if isinstance(value, dict):
                html += f"<p><strong>{key}:</strong></p><pre>{json.dumps(value, indent=2)}</pre>"
            else:
                html += f"<p><strong>{key}:</strong> {value}</p>"
        html += "</div>"

    html += """
        <p style='margin-top: 16px; font-size: 0.9em; color: #666;'>
            Use the buttons below to approve or deny this action.
        </p>
    </div>
    """

    return html


def handle_approval(approve: bool, token: str, approval_state: Dict, chat_history: List) -> Tuple[List, str, Dict]:
    """Handle user's approval or denial."""
    if not approval_state or "thread_id" not in approval_state:
        return chat_history, gr.update(visible=False), {}

    thread_id = approval_state["thread_id"]
    user_decision = "approved" if approve else "denied"

    # Send approval to backend
    result = make_request(
        "POST",
        "/agent/approve",
        token=token,
        data={
            "thread_id": thread_id,
            "approved": approve,
            "user_id": thread_id  # Using thread_id as user_id for simplicity in prototype
        }
    )

    if result["success"]:
        response_data = result["data"]
        agent_response = response_data.get("response", f"Action {user_decision}.")
        chat_history.append((f"[User {user_decision} the action]", agent_response))
    else:
        chat_history.append((f"[User {user_decision} the action]", f"❌ Error: {result['error']}"))

    return chat_history, gr.update(visible=False), {}


def connect_google_calendar(token: str) -> str:
    """Get Google OAuth URL and provide instructions."""
    if not token:
        return "❌ You must be logged in to connect a calendar."

    # Note: This endpoint doesn't exist yet (see BACKEND_CHANGE_REQUEST.md)
    result = make_request("GET", "/api/v1/auth/google/url", token=token)

    if result["success"]:
        auth_url = result["data"].get("auth_url")
        return f"""
        ✅ Google Calendar Connection:

        1. Open this URL in your browser:
        {auth_url}

        2. Grant calendar access

        3. You'll be redirected back to the app

        (This feature requires backend endpoint implementation - see BACKEND_CHANGE_REQUEST.md)
        """
    else:
        # Fallback for when endpoint doesn't exist yet
        return f"""
        📋 Google Calendar Connection (Mock):

        This feature requires the following backend endpoint to be implemented:
        GET /api/v1/auth/google/url

        See docs/BACKEND_CHANGE_REQUEST.md for details.

        For now, use the existing /auth/callback endpoint directly.
        """


def logout_user() -> Tuple[bool, Optional[str], str, str]:
    """Logout the user."""
    return False, None, gr.update(visible=False), "Logged out successfully. Please login again."


# Build the Gradio interface
with gr.Blocks(css=CUSTOM_CSS, title="Agentic ABP - Prototype") as app:
    # State management
    jwt_token = gr.State(None)
    is_authenticated = gr.State(False)
    thread_id = gr.State(None)
    approval_state = gr.State({})

    # Header
    gr.Markdown("""
    # 🤖 Agentic Administrative Business Partner
    ### Prototype v1.0 - Internal Testing Only

    This is a functional prototype connecting to the FastAPI backend.
    """)

    # Authentication Section
    with gr.Column(visible=True) as auth_section:
        gr.Markdown("## Please Login or Sign Up")

        with gr.Tabs() as auth_tabs:
            with gr.Tab("Login"):
                login_email = gr.Textbox(label="Email", placeholder="user@company.com")
                login_password = gr.Textbox(label="Password", type="password")
                login_btn = gr.Button("Login", variant="primary")
                login_status = gr.Markdown("")

            with gr.Tab("Sign Up"):
                signup_email = gr.Textbox(label="Email", placeholder="user@company.com")
                signup_password = gr.Textbox(label="Password", type="password")
                signup_domain = gr.Textbox(label="Internal Domain", placeholder="company.com")
                signup_timezone = gr.Textbox(
                    label="Timezone (Optional)",
                    placeholder="America/Los_Angeles",
                    value="America/Los_Angeles"
                )
                signup_btn = gr.Button("Create Account", variant="primary")
                signup_status = gr.Markdown("")

    # Main Chat Section
    with gr.Column(visible=False) as chat_section:
        gr.Markdown("## Chat with your Agentic ABP")

        # Chat interface
        chatbot = gr.Chatbot(
            label="Conversation",
            height=400,
            show_copy_button=True
        )

        # Approval card (hidden by default)
        approval_card = gr.HTML(visible=False)

        with gr.Row(visible=False) as approval_buttons_row:
            approve_btn = gr.Button("✅ Confirm / Proceed", variant="primary")
            deny_btn = gr.Button("❌ Deny / Cancel", variant="stop")

        # Input area
        with gr.Row():
            msg_input = gr.Textbox(
                label="Your message",
                placeholder="Ask me anything about your schedule...",
                scale=4
            )
            send_btn = gr.Button("Send", scale=1, variant="primary")

        # Action buttons
        with gr.Row():
            calendar_btn = gr.Button("🗓️ Connect Google Calendar")
            logout_btn = gr.Button("Logout", variant="secondary")

        calendar_status = gr.Markdown("")

    # Event handlers - Login
    login_btn.click(
        fn=login_user,
        inputs=[login_email, login_password],
        outputs=[login_status, is_authenticated, jwt_token, chat_section]
    ).then(
        fn=lambda: gr.update(visible=False),
        outputs=auth_section
    )

    # Event handlers - Signup
    signup_btn.click(
        fn=signup_user,
        inputs=[signup_email, signup_password, signup_domain, signup_timezone],
        outputs=[signup_status, is_authenticated, jwt_token, chat_section]
    )

    # Event handlers - Send message
    def send_and_update(message, token, history, tid):
        new_history, empty_msg, new_tid, approval_visible, approval_st = send_agent_query(
            message, token, history, tid
        )
        # Show approval buttons if approval is needed
        buttons_visible = gr.update(visible=approval_visible.value if hasattr(approval_visible, 'value') else False)
        return new_history, empty_msg, new_tid, approval_visible, approval_st, buttons_visible

    send_btn.click(
        fn=send_and_update,
        inputs=[msg_input, jwt_token, chatbot, thread_id],
        outputs=[chatbot, msg_input, thread_id, approval_card, approval_state, approval_buttons_row]
    )

    msg_input.submit(
        fn=send_and_update,
        inputs=[msg_input, jwt_token, chatbot, thread_id],
        outputs=[chatbot, msg_input, thread_id, approval_card, approval_state, approval_buttons_row]
    )

    # Event handlers - Approval
    approve_btn.click(
        fn=lambda token, state, history: handle_approval(True, token, state, history),
        inputs=[jwt_token, approval_state, chatbot],
        outputs=[chatbot, approval_card, approval_state]
    ).then(
        fn=lambda: gr.update(visible=False),
        outputs=approval_buttons_row
    )

    deny_btn.click(
        fn=lambda token, state, history: handle_approval(False, token, state, history),
        inputs=[jwt_token, approval_state, chatbot],
        outputs=[chatbot, approval_card, approval_state]
    ).then(
        fn=lambda: gr.update(visible=False),
        outputs=approval_buttons_row
    )

    # Event handlers - Calendar
    calendar_btn.click(
        fn=connect_google_calendar,
        inputs=[jwt_token],
        outputs=[calendar_status]
    )

    # Event handlers - Logout
    logout_btn.click(
        fn=logout_user,
        outputs=[is_authenticated, jwt_token, chat_section, login_status]
    ).then(
        fn=lambda: gr.update(visible=True),
        outputs=auth_section
    )

    # Footer
    gr.Markdown("""
    ---
    **Instructions:**
    1. Sign up with an email, password, and internal domain (e.g., `company.com`)
    2. Login with your credentials
    3. Start chatting with your agent
    4. Connect your Google Calendar when prompted
    5. Review and approve any actions that require your permission

    **Backend Status:** Make sure the FastAPI server is running at `http://localhost:8000`

    For production deployment, see the React front-end in `frontend/` directory.
    """)

# Launch configuration
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  Agentic ABP - Gradio Prototype                              ║
    ║  Version: 1.0                                                ║
    ╚══════════════════════════════════════════════════════════════╝

    Starting Gradio server...

    Prerequisites:
    1. FastAPI backend must be running at http://localhost:8000
       Run: uvicorn src.main_refactored:app --reload

    2. Set API_BASE_URL environment variable if backend is elsewhere:
       export API_BASE_URL=http://your-backend:8000

    3. Ensure the backend has the latest changes:
       - /agent/invoke now returns full AgentResponse
       - ApprovalRequest supports edited_email_body

    """)

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )
