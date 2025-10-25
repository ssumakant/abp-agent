# Quick Reference Guide
## Agentic ABP Front-End

**For**: Developers, QA, Product Managers
**Updated**: October 24, 2025

---

## 🚀 Quick Start Commands

### Gradio (Testing)
```bash
pip install gradio requests
python gradio_app.py
# → http://localhost:7860
```

### React (Production)
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Backend
```bash
uvicorn src.main_refactored:app --reload
# → http://localhost:8000
```

---

## 📁 Where is Everything?

| Item | Location |
|------|----------|
| **Gradio App** | `gradio_app.py` (single file) |
| **React App** | `frontend/` directory |
| **Backend API** | `src/main_refactored.py` |
| **Design Doc** | `docs/FRONTEND_DESIGN_DOCUMENT.md` |
| **Backend CR** | `docs/BACKEND_CHANGE_REQUEST.md` |
| **Gradio Guide** | `docs/implementation/GRADIO_IMPLEMENTATION.md` |
| **React Guide** | `docs/implementation/REACT_IMPLEMENTATION.md` |
| **Component Catalog** | `docs/implementation/COMPONENT_CATALOG.md` |

---

## 🎯 Which Front-End Should I Use?

| Scenario | Use |
|----------|-----|
| Testing backend changes | **Gradio** |
| Internal demo | **Gradio** |
| Debugging agent logic | **Gradio** |
| Investor presentation | **React** |
| Production deployment | **React** |
| Full feature showcase | **React** |

---

## 🧭 User Flows

### Flow 1: Sign Up & Login

```
Gradio:
1. Open http://localhost:7860
2. Click "Sign Up" tab
3. Fill: email, password, domain
4. Create account
5. Switch to "Login" tab
6. Enter credentials
7. Click "Login"

React:
1. Open http://localhost:3000
2. Click "Sign up" link
3. Fill form
4. Submit
5. Click "Sign in" link
6. Enter credentials
7. Submit → redirects to /chat
```

### Flow 2: Chat with Agent

```
1. Type message: "Am I free tomorrow?"
2. Press Enter or click Send
3. Agent responds
4. Continue conversation
```

### Flow 3: Approval Flow

```
1. Request action that violates rule
   Example: "Book meeting on Saturday"
2. Agent shows approval card
3. Review details
4. Click "Confirm" or "Deny"
5. Agent executes or cancels
```

### Flow 4: Settings (React Only)

```
1. Click settings gear icon in header
2. View connected accounts
3. Click "Add New Account" (mock)
4. Adjust work hours
5. Set busyness threshold
6. Add protected time blocks
7. Toggle weekend meetings
8. Click "Save Changes"
```

---

## 🔑 API Endpoints

### Available (Implemented)

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/token` | POST | No | Login (OAuth2 form) |
| `/users` | POST | No | Create account |
| `/agent/invoke` | POST | Yes | Send query to agent |
| `/agent/approve` | POST | Yes | Approval response |

### Missing (Mocked in React)

| Endpoint | Method | Purpose | See |
|----------|--------|---------|-----|
| `/api/v1/settings` | GET | Get constitution | BACKEND_CHANGE_REQUEST.md |
| `/api/v1/settings` | POST | Update constitution | BACKEND_CHANGE_REQUEST.md |
| `/api/v1/auth/google/url` | GET | OAuth URL | BACKEND_CHANGE_REQUEST.md |
| `/api/v1/auth/accounts` | GET | List accounts | BACKEND_CHANGE_REQUEST.md |
| `/api/v1/auth/accounts/:id` | DELETE | Remove account | BACKEND_CHANGE_REQUEST.md |

---

## 💾 State Management (React)

### useAuthStore
```typescript
const { isAuthenticated, userEmail, login, logout } = useAuthStore()
```

### useChatStore
```typescript
const {
  messages,
  isLoading,
  pendingApproval,
  sendMessage,
  handleApproval
} = useChatStore()
```

### useSettingsStore
```typescript
const {
  settings,
  connectedAccounts,
  fetchSettings,
  updateSettings
} = useSettingsStore()
```

---

## 🎨 Component Quick Reference

### Atoms
```typescript
<Button variant="default">Click</Button>
<Input placeholder="Enter text" />
<Label>Field Label</Label>
<Card><CardContent>Content</CardContent></Card>
<Dialog open={isOpen}><DialogContent>...</DialogContent></Dialog>
<Switch checked={value} onCheckedChange={setValue} />
<Textarea />
```

### Molecules
```typescript
<FormField label="Email" value={email} onChange={setEmail} />
<MessageBubble message={message} />
```

### Organisms
```typescript
<MessageList messages={messages} isLoading={loading} />
<ChatInputForm onSend={handleSend} />
```

### Features
```typescript
<LoginForm />
<SignupForm onSuccess={handleSuccess} />
<ApprovalRequestCard
  approvalType="constitution_override"
  approvalData={data}
  onApprove={approve}
  onDeny={deny}
/>
<DraftEmailReviewModal
  isOpen={show}
  draftedEmail={email}
  onSend={send}
/>
<ConstitutionForm />
<ConnectedAccountsList />
```

---

## 🛠️ Common Tasks

### Add a New Page (React)

1. Create page: `src/pages/NewPage.tsx`
2. Add route in `App.tsx`:
   ```typescript
   <Route path="/new" element={
     <ProtectedRoute><NewPage /></ProtectedRoute>
   } />
   ```
3. Add navigation:
   ```typescript
   <Button onClick={() => navigate('/new')}>Go</Button>
   ```

### Add a New Store (React)

1. Create file: `src/store/useNewStore.ts`
2. Define interface and implementation:
   ```typescript
   interface NewState {
     data: any
     fetchData: () => Promise<void>
   }

   export const useNewStore = create<NewState>((set) => ({
     data: null,
     fetchData: async () => {
       const data = await api.getData()
       set({ data })
     }
   }))
   ```
3. Use in component:
   ```typescript
   const { data, fetchData } = useNewStore()
   ```

### Add a New Component (React)

1. Choose layer (atom/molecule/organism/feature)
2. Create file in appropriate directory
3. Define props interface
4. Implement component
5. Export from index file (optional)

### Add API Endpoint (React)

1. Add type in `src/types/index.ts`
2. Add function in `src/services/apiClient.ts`:
   ```typescript
   export async function newEndpoint(param: string): Promise<Response> {
     const response = await axiosInstance.get(`/api/new/${param}`)
     return response.data
   }
   ```
3. Use in store or component:
   ```typescript
   const data = await api.newEndpoint('value')
   ```

---

## 🐛 Troubleshooting

### Backend not responding

**Check**:
```bash
curl http://localhost:8000/health
```

**Fix**:
```bash
uvicorn src.main_refactored:app --reload
```

### Gradio: Login fails

**Check**: Backend logs for errors

**Common issues**:
- User doesn't exist (sign up first)
- Wrong password
- Backend not running

### React: CORS errors

**Solution**: Backend already configured for CORS, check:
1. Backend is running
2. Correct API_BASE_URL in `.env`
3. Network tab in browser dev tools

### React: 401 Unauthorized

**Solution**:
```javascript
// Clear localStorage
localStorage.clear()
// Refresh page
// Re-login
```

### React: Settings not saving

**Solution**: Endpoint not implemented yet
- Check console for "Using mocked endpoint" warning
- Settings use mock data until backend implements endpoints
- See `BACKEND_CHANGE_REQUEST.md`

### Gradio: State lost on refresh

**Expected behavior**: Gradio stores state in memory only
**Solution**: Re-login after refresh

---

## 📊 Testing Scenarios

### Test 1: Basic Chat
```
1. Login
2. Type: "Hello"
3. Verify: Agent responds
4. Type: "Am I free tomorrow at 2pm?"
5. Verify: Agent checks calendar
```

### Test 2: Constitution Override
```
1. Login
2. Type: "Book a meeting this Saturday"
3. Verify: Approval card appears (red border)
4. Verify: Shows "No weekend meetings" rule
5. Click "Confirm"
6. Verify: Meeting scheduled
```

### Test 3: Reschedule Flow
```
1. Login
2. Type: "I need to free up time next week"
3. Verify: Agent analyzes schedule
4. Verify: Suggests meeting to reschedule
5. Verify: Shows approval card (yellow border)
6. Click "Proceed"
7. Verify: Email review modal appears
8. Edit email body
9. Click "Send and Reschedule"
10. Verify: Success message
```

### Test 4: Settings Management (React Only)
```
1. Login
2. Click settings gear icon
3. Change work hours to 8am-6pm
4. Adjust busyness threshold to 80%
5. Add protected block "Lunch" 12pm-1pm
6. Click "Save Changes"
7. Verify: Success message
```

---

## 🔐 Security Notes

### JWT Token
- **Stored**: localStorage (React), gr.State (Gradio)
- **Expiry**: 30 minutes default
- **Auto-refresh**: On API calls
- **Logout**: Clears token and redirects

### Best Practices
- Always use HTTPS in production
- Never log JWT tokens
- Clear token on logout
- Handle 401 errors (auto-logout)

---

## 🚀 Deployment Checklist

### Pre-Deployment (React)

- [ ] Run `npm run build`
- [ ] Test production build: `npm run preview`
- [ ] Set `VITE_API_BASE_URL` to production API
- [ ] Set `VITE_ENABLE_MOCK_API=false`
- [ ] Test all user flows
- [ ] Check console for errors
- [ ] Test mobile responsiveness
- [ ] Verify accessibility

### Deploy to Vercel

```bash
cd frontend
vercel

# Set environment variables in Vercel dashboard:
# VITE_API_BASE_URL=https://api.yourdomain.com
```

### Deploy to Netlify

```bash
cd frontend
npm run build
netlify deploy --prod --dir=dist

# Set environment variables in Netlify dashboard
```

---

## 📞 Getting Help

| Question | Resource |
|----------|----------|
| How do I... | Check this Quick Reference |
| Component API? | `docs/implementation/COMPONENT_CATALOG.md` |
| Architecture? | `docs/FRONTEND_DESIGN_DOCUMENT.md` |
| Gradio details? | `docs/implementation/GRADIO_IMPLEMENTATION.md` |
| React details? | `docs/implementation/REACT_IMPLEMENTATION.md` |
| Backend changes? | `docs/BACKEND_CHANGE_REQUEST.md` |
| General overview? | `DELIVERABLES_SUMMARY.md` |

---

## 🎓 Learning Resources

### React/TypeScript
- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Libraries
- [Zustand](https://github.com/pmndrs/zustand)
- [React Router](https://reactrouter.com)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)

### Gradio
- [Gradio Docs](https://gradio.app/docs)

---

## 🎯 Quick Commands Reference

```bash
# Gradio
python gradio_app.py                    # Run Gradio

# React
cd frontend
npm install                             # Install dependencies
npm run dev                             # Development server
npm run build                           # Production build
npm run preview                         # Preview build
npm run type-check                      # TypeScript check

# Backend
uvicorn src.main_refactored:app --reload  # Development
python -m pytest tests/                   # Run tests

# Git
git status                              # Check status
git add .                               # Stage all
git commit -m "message"                 # Commit
git push                                # Push

# Environment
cp frontend/.env.example frontend/.env  # Copy env template
```

---

**Last Updated**: October 24, 2025
**Version**: 1.0
**Status**: Production-Ready
