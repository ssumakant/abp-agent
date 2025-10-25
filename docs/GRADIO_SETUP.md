# Gradio Prototype Setup Guide

Quick and dirty functional prototype for internal testing of the Agentic ABP agent.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Backend API running at `http://localhost:8000`

### Installation

```bash
# From the project root
cd /home/user/abp-agent

# Install Gradio and dependencies
pip install gradio requests

# Run the Gradio app
python gradio_app.py
```

The Gradio interface will open automatically in your browser at `http://localhost:7860`

---

## 📋 Features

### 1. Authentication
- **Login Tab**: Existing users can log in with email/password
- **Sign Up Tab**: New users can create accounts with email, password, and internal domain

### 2. Conversational Interface
- Chat with the agent after logging in
- View conversation history
- Real-time responses from the backend

### 3. Approval Flow
- Visual approval cards for actions requiring confirmation
- Approve/Deny buttons
- Context-specific approval messages

### 4. Google Calendar Connection
- Button to initiate OAuth flow (requires backend endpoint)
- Instructions for connecting calendar accounts

---

## 🎨 UI Components

### Login/Signup (Tabs)
- Email input
- Password input (hidden)
- Internal domain input (signup only)
- Timezone input (signup only, optional)

### Chat Interface
- Chatbot component showing conversation history
- Text input for user messages
- Send button

### Approval Cards
- Dynamic HTML cards based on approval type
- Constitution overrides (red/warning style)
- Meeting rescheduling (yellow/info style)
- Contextual information display

### Action Buttons
- Connect Google Calendar
- Logout

---

## 🔧 Configuration

### Environment Variable

Set the backend URL if different from default:

```bash
export API_BASE_URL=http://your-backend:8000
python gradio_app.py
```

### Custom CSS

The app includes custom CSS for branding:
- Approval cards styled by type
- Success/error message styling
- Responsive layout

---

## 💡 Usage Examples

### 1. Sign Up

1. Navigate to "Sign Up" tab
2. Enter email: `user@company.com`
3. Enter password: `secure_password`
4. Enter domain: `company.com`
5. (Optional) Enter timezone: `America/Los_Angeles`
6. Click "Create Account"
7. Switch to "Login" tab after success message

### 2. Login

1. Navigate to "Login" tab
2. Enter your email and password
3. Click "Login"
4. Chat interface appears

### 3. Chat with Agent

1. Type a message: "Am I free tomorrow at 2pm?"
2. Click "Send" or press Enter
3. Agent responds with availability

### 4. Handle Approval

When an action requires approval:

1. Agent shows approval card with context
2. Review the information
3. Click "✅ Confirm / Proceed" to approve
4. OR click "❌ Deny / Cancel" to reject
5. Agent executes action or confirms cancellation

---

## 🐛 Known Limitations

### Gradio Constraints

1. **No Modal Dialogs**: Email review shown inline, not as popup
2. **Limited Styling**: Cannot perfectly match wireframes
3. **Basic State Management**: `gr.State` is simple key-value storage
4. **No Persistent Sessions**: Refresh clears state
5. **Single Thread**: No multi-conversation support

### Workarounds

- **Email Review**: Show drafted email in approval card instead of modal
- **Styling**: Use custom CSS for basic branding
- **State**: Store JWT token in `gr.State` for session

---

## 🔌 API Integration

### Backend Calls

The Gradio app uses the following endpoints:

1. **POST /token** - Login (OAuth2 form data)
2. **POST /users** - Create account (JSON)
3. **POST /agent/invoke** - Send agent query (JSON with Bearer token)
4. **POST /agent/approve** - Send approval response (JSON with Bearer token)

### Request Examples

#### Login
```python
requests.post(
    "http://localhost:8000/token",
    data={"username": email, "password": password}
)
```

#### Agent Query
```python
requests.post(
    "http://localhost:8000/agent/invoke",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": "Find time for a meeting tomorrow"}
)
```

---

## 🚧 Missing Features (Compared to React Version)

1. **No Settings Page**: Constitution management not implemented
2. **No Account Management**: Cannot connect/disconnect Google accounts
3. **No Thread Management**: Single conversation only
4. **Limited UI Customization**: Cannot match exact wireframe design
5. **No Optimistic Updates**: Loading states basic

---

## 🎯 Use Cases

### Internal Testing
- Test backend API functionality
- Verify agent responses
- Test approval flow logic
- Debug issues quickly

### Demo Purposes
- Show basic functionality to stakeholders
- Quick prototype for feedback
- Validate user experience flow

### Development
- Frontend developers testing backend
- Backend developers testing their endpoints
- QA testing without full React setup

---

## 🔄 Refresh Behavior

**Important**: Refreshing the browser will:
- Clear the JWT token
- Clear conversation history
- Reset to login screen

For persistent sessions, use the React front-end.

---

## 📊 Comparison: Gradio vs React

| Feature | Gradio | React |
|---------|--------|-------|
| Setup Time | 5 minutes | 30 minutes |
| Authentication | ✅ Basic | ✅ Full |
| Chat Interface | ✅ Basic | ✅ Advanced |
| Approval Flow | ✅ Cards inline | ✅ Cards + Modals |
| Settings Page | ❌ No | ✅ Yes |
| Multi-threading | ❌ No | ✅ Yes |
| Custom Styling | ⚠️ Limited | ✅ Full Control |
| Production Ready | ❌ No | ✅ Yes |
| Investor Demo | ⚠️ OK | ✅ Excellent |

---

## 🐞 Troubleshooting

### Issue: "Cannot connect to backend"

**Symptom**: Login fails with connection error

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend if not running
uvicorn src.main_refactored:app --reload
```

### Issue: "Login failed: 401"

**Symptom**: Invalid username or password

**Solution**:
1. Verify user exists (sign up first)
2. Check password is correct
3. Check backend logs for errors

### Issue: Approval buttons not working

**Symptom**: Clicking approve/deny does nothing

**Solution**:
1. Check browser console for errors
2. Verify `thread_id` is being stored correctly
3. Check backend `/agent/approve` endpoint

### Issue: Custom CSS not loading

**Symptom**: App looks plain/unstyled

**Solution**:
- CSS is embedded in the Python file
- No external files needed
- Check `CUSTOM_CSS` variable in `gradio_app.py`

---

## 🔐 Security Notes

**This is a prototype for internal testing only. DO NOT use in production.**

- JWT tokens stored in `gr.State` (memory only)
- No HTTPS required for localhost
- No rate limiting
- No input validation (handled by backend)

For production, use the React front-end.

---

## 📞 Support

### Issues

- **Backend errors**: Check backend logs
- **Gradio errors**: Check terminal running `gradio_app.py`
- **Browser errors**: Check browser console (F12)

### Getting Help

- Slack: #apb-agent-development
- Backend docs: `docs/ARCHITECTURE.md`
- API docs: http://localhost:8000/docs

---

## 🎓 Next Steps

Once you've tested the Gradio prototype:

1. Review the UX/UI Design Spec
2. Compare with React implementation
3. Test both front-ends
4. Provide feedback on Slack
5. Check `BACKEND_CHANGE_REQUEST.md` for missing endpoints

---

## 📝 Code Structure

```python
# gradio_app.py structure

1. Imports and Configuration
2. Helper Functions (API calls)
3. Authentication Functions
4. Agent Query Functions
5. Approval Functions
6. Gradio Interface (gr.Blocks)
7. Event Handlers
8. Launch Configuration
```

Simple, single-file design for easy understanding and modification.

---

## 🚀 Future Enhancements (If Needed)

Possible improvements for the Gradio version:

1. **Persistent Sessions**: Use cookies or browser storage
2. **Settings Tab**: Add basic constitution management
3. **Thread Sidebar**: Show conversation history
4. **Rich Formatting**: Better message display
5. **File Upload**: Support attachments

However, for these features, **the React version is recommended**.

---

## ✅ Checklist for Testing

- [ ] Can sign up new users
- [ ] Can log in existing users
- [ ] Can send messages to agent
- [ ] Agent responses appear correctly
- [ ] Approval cards display when needed
- [ ] Can approve actions
- [ ] Can deny actions
- [ ] Logout works
- [ ] Reconnect after logout works

---

## 📄 File Location

**Single file**: `/home/user/abp-agent/gradio_app.py`

That's it! Everything is self-contained.
