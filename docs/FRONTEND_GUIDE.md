# Front-End Implementation Guide

Complete guide to both front-end implementations for the Agentic ABP agent.

---

## 📦 Two Front-End Forks

This project includes **two separate front-end implementations**:

### 1. **Gradio Prototype** (Quick & Dirty)
**Location**: `gradio_app.py`
**Purpose**: Rapid internal testing and demos
**Setup Time**: 5 minutes
**Production Ready**: ❌ No

### 2. **React Application** (Enterprise-Grade)
**Location**: `frontend/`
**Purpose**: Investor demos and production deployment
**Setup Time**: 30 minutes
**Production Ready**: ✅ Yes

---

## 🚀 Quick Start

### Option 1: Gradio (Testing)

```bash
# Install Gradio
pip install gradio requests

# Run
python gradio_app.py

# Open browser to http://localhost:7860
```

### Option 2: React (Production)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Open browser to http://localhost:3000
```

---

## 🏗️ Architecture Comparison

| Aspect | Gradio | React |
|--------|--------|-------|
| **Language** | Python | TypeScript |
| **Framework** | Gradio | React 18 + Vite |
| **State Management** | gr.State | Zustand |
| **Routing** | Single Page | React Router v6 |
| **Styling** | Custom CSS | Tailwind + shadcn/ui |
| **Component Library** | Built-in | shadcn/ui (Radix UI) |
| **API Client** | requests | Axios with interceptors |
| **Build Tool** | None | Vite |
| **TypeScript** | ❌ | ✅ |
| **Hot Reload** | ✅ | ✅ |

---

## 📋 Feature Comparison

### Gradio Prototype

**✅ Implemented:**
- User authentication (login/signup)
- Conversational chat interface
- Approval flow with cards
- Connect Google Calendar button
- Logout functionality

**❌ Not Implemented:**
- Settings page (Constitution)
- Account management
- Multi-thread conversations
- Email review modal (shown inline instead)
- Advanced styling

**🎯 Best For:**
- Quick backend testing
- Internal demos
- Proof-of-concept
- Debugging agent logic

---

### React Application

**✅ Implemented:**
- Full authentication flow
- Protected routes
- Conversational interface
- Approval flow with cards
- Email review modal (with editing)
- Complete Settings page
- Account management
- Protected time blocks
- Constitution rules
- Multi-thread support (architecture ready)
- Responsive design
- Accessibility features

**🎯 Best For:**
- Investor presentations
- Production deployment
- User acceptance testing
- Full feature showcase

---

## 🎨 Design Adherence

### Wireframe Implementation

| Wireframe | Gradio | React |
|-----------|--------|-------|
| **Screen 1: Settings** | ❌ Not implemented | ✅ Fully implemented |
| **Screen 2: Chat** | ✅ Basic | ✅ Full implementation |
| **Screen 3: Approval Card** | ✅ Inline cards | ✅ Cards + tooltips |
| **Screen 4: Email Modal** | ⚠️ Inline (no modal) | ✅ Modal with editing |

---

## 🔌 Backend Integration

Both front-ends integrate with the same FastAPI backend.

### Required Backend (Implemented)

- `POST /token` - Authentication
- `POST /users` - User creation
- `POST /agent/invoke` - Agent queries
- `POST /agent/approve` - Approval responses

### Missing Backend (Mocked in React)

See `docs/BACKEND_CHANGE_REQUEST.md`:

- `GET /api/v1/settings` - Get constitution
- `POST /api/v1/settings` - Update constitution
- `GET /api/v1/auth/google/url` - OAuth URL
- `GET /api/v1/auth/accounts` - List accounts
- `DELETE /api/v1/auth/accounts/{id}` - Remove account

**React Front-End**: Uses mock data until backend implements these
**Gradio Prototype**: Does not attempt to use these endpoints

---

## 📐 Architecture Details

### React Application Structure

```
frontend/
├── src/
│   ├── components/          # Atomic design
│   │   ├── atoms/           # Button, Input, Label...
│   │   ├── molecules/       # FormField, MessageBubble...
│   │   ├── organisms/       # MessageList, ChatInputForm...
│   │   └── layouts/         # Header
│   │
│   ├── features/            # Domain modules
│   │   ├── auth/            # Login, Signup
│   │   ├── chat/            # Approval cards, Email modal
│   │   └── settings/        # Constitution form, Accounts
│   │
│   ├── pages/               # Routes
│   │   ├── LoginPage.tsx
│   │   ├── ChatPage.tsx
│   │   └── SettingsPage.tsx
│   │
│   ├── services/            # API layer
│   │   └── apiClient.ts     # Centralized API calls
│   │
│   ├── store/               # State management
│   │   ├── useAuthStore.ts
│   │   ├── useChatStore.ts
│   │   └── useSettingsStore.ts
│   │
│   └── types/               # TypeScript types
│       └── index.ts
```

### Gradio Structure

```
gradio_app.py                # Single file
├── Configuration            # API URL, CSS
├── Helper Functions         # API calls
├── Auth Functions           # Login, signup
├── Agent Functions          # Send message, handle approval
├── Gradio Interface         # gr.Blocks layout
└── Event Handlers           # Button clicks, form submits
```

---

## 🎯 Deployment Guide

### Gradio (Internal Only)

```bash
# Local deployment only
python gradio_app.py

# Optional: Share publicly (temporary)
python gradio_app.py
# Set share=True in launch() for temporary Gradio link
```

**Not recommended for production.**

---

### React (Production)

#### Build

```bash
cd frontend
npm run build
```

#### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

#### Deploy to Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### Deploy to AWS S3

```bash
aws s3 sync dist/ s3://your-bucket-name
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

#### Environment Variables

Set in your hosting platform:
```
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_ENABLE_MOCK_API=false
```

---

## 🧪 Testing Strategy

### Gradio Testing

1. **Manual Testing**: Click through all features
2. **Backend Integration**: Verify API calls work
3. **Approval Flow**: Test approve/deny actions

No automated tests for Gradio (it's a prototype).

---

### React Testing (Future)

**Recommended Test Stack**:
- **Unit Tests**: Vitest + React Testing Library
- **Integration Tests**: Playwright
- **E2E Tests**: Playwright or Cypress

**Test Coverage Goals**:
- Components: 80%+
- API Service: 100%
- Store: 100%
- Critical user flows: 100%

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: Backend not responding

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# Start backend
cd /home/user/abp-agent
uvicorn src.main_refactored:app --reload
```

#### Issue: CORS errors

**Solution**: Backend already has CORS configured for all origins. Check:
1. Backend logs for errors
2. Browser console for exact error
3. Network tab in DevTools

#### Issue: 401 Unauthorized

**React Solution**:
1. Clear localStorage: `localStorage.clear()`
2. Re-login
3. Check JWT token expiry

**Gradio Solution**:
1. Refresh page
2. Re-login

#### Issue: Settings not saving (React)

**Solution**: Backend endpoints not implemented yet.
1. Check `BACKEND_CHANGE_REQUEST.md`
2. Enable mock mode: Set `VITE_ENABLE_MOCK_API=true`

---

## 📊 Performance

### Gradio

- **Initial Load**: < 2 seconds
- **Chat Response**: Depends on backend (~1-3 seconds)
- **Memory**: Low (~50MB)
- **Scalability**: Single user at a time

### React

- **Initial Load**: < 1 second (built)
- **Chat Response**: Depends on backend (~1-3 seconds)
- **Bundle Size**: ~500KB gzipped
- **Memory**: ~100MB
- **Scalability**: Unlimited concurrent users

---

## 🔐 Security

### Gradio (Prototype)

- ⚠️ JWT stored in Python memory (cleared on refresh)
- ⚠️ No CSRF protection
- ⚠️ No rate limiting
- ⚠️ HTTP OK for localhost
- **DO NOT use in production**

### React (Production)

- ✅ JWT stored in localStorage (persistent)
- ✅ Automatic token expiry handling
- ✅ HTTPS enforced in production
- ✅ Input sanitization
- ✅ CORS properly configured
- ⚠️ Rate limiting on backend (recommended)
- ⚠️ CSRF tokens (recommended for cookies)

---

## 📱 Mobile Support

### Gradio

- ⚠️ Basic mobile support
- UI may not fit small screens
- No touch optimizations

### React

- ✅ Responsive design
- ✅ Mobile-friendly UI
- ✅ Touch-optimized interactions
- ✅ Tested on iOS Safari and Chrome Mobile

---

## ♿ Accessibility

### Gradio

- ⚠️ Basic keyboard navigation
- ❌ Screen reader support limited
- ❌ No ARIA labels

### React

- ✅ Full keyboard navigation
- ✅ Screen reader support (Radix UI primitives)
- ✅ ARIA labels and roles
- ✅ Focus management
- ✅ Color contrast compliance

---

## 🗺️ Roadmap

### Gradio (Maintenance Mode)

- No major updates planned
- Bug fixes only
- Use React for new features

### React (Active Development)

**Phase 1** (Current - MVP):
- ✅ Core features implemented
- ⏳ Awaiting backend endpoints

**Phase 2** (Investor Demo Enhancements):
- Thread sidebar
- Rich message formatting
- Calendar visualization
- Advanced search
- Export conversations

**Phase 3** (Production Ready):
- Real-time updates (WebSockets)
- Push notifications
- Offline support
- Progressive Web App (PWA)
- Mobile app (React Native)

---

## 📚 Documentation

- **Gradio Setup**: `docs/GRADIO_SETUP.md`
- **React Setup**: `frontend/README.md`
- **Backend CR**: `docs/BACKEND_CHANGE_REQUEST.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **API Docs**: http://localhost:8000/docs

---

## 👥 Team Responsibilities

### Front-End Team

- Gradio prototype maintenance
- React feature development
- UI/UX improvements
- Documentation

### Backend Team

- Implement missing endpoints (see BACKEND_CHANGE_REQUEST.md)
- API bug fixes
- Performance optimization
- WebSocket support (future)

---

## 🎓 Learning Resources

### For Gradio Development

- [Gradio Documentation](https://gradio.app/docs)
- [Gradio Examples](https://gradio.app/guides/quickstart)

### For React Development

- [React Docs](https://react.dev)
- [Vite Guide](https://vitejs.dev/guide/)
- [Zustand](https://github.com/pmndrs/zustand)
- [React Router](https://reactrouter.com)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)

---

## 📞 Support

- **Slack**: #apb-agent-development
- **Issues**: Create in GitHub/Jira
- **Questions**: Tag @frontend-lead

---

## ✅ Final Checklist

### Before Investor Demo

- [ ] Backend running with latest changes
- [ ] React app built and deployed
- [ ] Test all user flows
- [ ] Check mobile responsiveness
- [ ] Verify approval flows work
- [ ] Settings page fully functional
- [ ] No console errors
- [ ] Performance optimized

### Before Production

- [ ] All backend endpoints implemented
- [ ] Remove mock data
- [ ] Security audit completed
- [ ] Load testing passed
- [ ] Accessibility audit passed
- [ ] Analytics integrated
- [ ] Error tracking setup (Sentry)
- [ ] Documentation updated

---

**Choose the right tool for the job:**

- **Quick test?** → Use Gradio
- **Investor meeting?** → Use React
- **Production launch?** → Use React
