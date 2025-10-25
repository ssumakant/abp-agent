# Agentic ABP - React Front-End

Enterprise-grade, investor-ready front-end for the Agentic Administrative Business Partner (ABP) application.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running at `http://localhost:8000`

### Installation

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── atoms/           # Basic building blocks (Button, Input, etc.)
│   │   ├── molecules/       # Combinations of atoms (FormField, MessageBubble)
│   │   ├── organisms/       # Complex components (MessageList, ChatInputForm)
│   │   └── layouts/         # Layout components (Header)
│   │
│   ├── features/            # Domain-specific feature modules
│   │   ├── auth/            # Authentication (LoginForm, SignupForm)
│   │   ├── chat/            # Chat features (ApprovalCard, EmailModal)
│   │   └── settings/        # Settings features (ConstitutionForm, AccountsList)
│   │
│   ├── pages/               # Route-level page components
│   │   ├── LoginPage.tsx
│   │   ├── ChatPage.tsx
│   │   └── SettingsPage.tsx
│   │
│   ├── services/            # API communication layer
│   │   └── apiClient.ts     # Centralized API service
│   │
│   ├── store/               # Zustand state management
│   │   ├── useAuthStore.ts
│   │   ├── useChatStore.ts
│   │   └── useSettingsStore.ts
│   │
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   │
│   ├── utils/               # Utility functions
│   │   └── cn.ts            # Tailwind class merger
│   │
│   ├── App.tsx              # Main application component with routing
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles and Tailwind imports
│
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── vite.config.ts
└── README.md
```

---

## 🏗️ Architecture

### State Management (Zustand)

We use Zustand for lightweight, performant state management:

- **useAuthStore**: Manages authentication state and JWT token
- **useChatStore**: Manages conversation history, messages, and approval flow
- **useSettingsStore**: Manages user settings/constitution

### Routing (React Router v6)

- `/` - Login/Signup page (public)
- `/chat` - Main conversational interface (protected)
- `/settings` - Constitution/settings page (protected)

### API Service Layer

All API calls are centralized in `src/services/apiClient.ts`:
- Automatic JWT token injection via Axios interceptors
- Centralized error handling
- Mock data support for endpoints not yet implemented
- Type-safe with TypeScript

### Component Design (Atomic Design)

- **Atoms**: Basic UI elements (Button, Input, Card)
- **Molecules**: Simple combinations (FormField, MessageBubble)
- **Organisms**: Complex components (MessageList, ChatInputForm)
- **Features**: Domain-specific components (LoginForm, ApprovalCard)
- **Pages**: Route-level components (LoginPage, ChatPage)

---

## 🎨 Design System

### UI Library

We use **shadcn/ui** components built on:
- **Radix UI** primitives for accessibility
- **Tailwind CSS** for styling
- **class-variance-authority** for component variants

### Color Palette

Defined in `src/index.css` using CSS variables:
- Primary: Blue (`hsl(221.2 83.2% 53.3%)`)
- Destructive: Red (`hsl(0 84.2% 60.2%)`)
- Background: White
- Muted: Gray tones

### Typography

- Font: System fonts (Inter-like)
- Scale: Tailwind's default typography scale

---

## 🔐 Authentication Flow

1. User visits `/` (LoginPage)
2. Login/Signup via API
3. JWT token stored in localStorage
4. Axios interceptor adds token to all requests
5. On 401 error, auto-logout and redirect to `/`

---

## 💬 Conversational Interface

### Main Chat Flow

1. User types message in ChatInputForm
2. `useChatStore.sendMessage()` sends to `/agent/invoke`
3. Response displayed as agent message
4. If `requires_approval`, show ApprovalRequestCard

### Approval Flow Types

#### 1. Constitution Override
```typescript
{
  requires_approval: true,
  approval_type: "constitution_override",
  approval_data: {
    rule_violated: "No business meetings on weekends"
  }
}
```

#### 2. Reschedule Meeting
```typescript
{
  requires_approval: true,
  approval_type: "reschedule_meeting",
  approval_data: {
    chosen_meeting: { /* meeting object */ },
    proposed_new_time: "2025-10-25T14:00:00Z"
  }
}
```

#### 3. Email Review
```typescript
{
  requires_approval: true,
  approval_type: "email_review",
  approval_data: {
    drafted_email: {
      to: "colleague@company.com",
      subject: "Rescheduling our meeting",
      body: "Hi..."
    }
  }
}
```

User approves → `POST /agent/approve` with optional `edited_email_body`

---

## ⚙️ Settings Page (The Constitution)

### Features

1. **Connected Accounts**
   - List Google Calendar accounts
   - Add new accounts (OAuth flow)
   - Remove accounts

2. **Schedule Density**
   - Set work hours (start/end time)
   - Busyness threshold (slider 0-100%)

3. **Scheduling Rules**
   - Toggle: No weekend meetings

4. **Protected Time Blocks**
   - Add/remove custom time blocks
   - Define name, start/end time, days

### Data Flow

1. On load: `fetchSettings()` → `GET /api/v1/settings`
2. User edits form
3. Click "Save Changes" → `updateSettings()` → `POST /api/v1/settings`

---

## 🔌 Backend Integration

### Available Endpoints (Implemented)

- `POST /token` - Login
- `POST /users` - Sign up
- `POST /agent/invoke` - Agent queries
- `POST /agent/approve` - Approval responses

### Missing Endpoints (Mocked)

See `docs/BACKEND_CHANGE_REQUEST.md` for implementation details:

- `GET /api/v1/settings`
- `POST /api/v1/settings`
- `GET /api/v1/auth/google/url`
- `GET /api/v1/auth/accounts`
- `DELETE /api/v1/auth/accounts/{id}`

**Mock Mode**: Set `VITE_ENABLE_MOCK_API=true` in `.env` to use mock data

---

## 🛠️ Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run type-check

# Lint code
npm run lint
```

### Environment Variables

Create `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_MOCK_API=false
```

---

## 🚢 Deployment

### Build for Production

```bash
npm run build
```

Output in `dist/` directory.

### Deployment Options

#### 1. Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

#### 2. Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### 3. Static Hosting

Upload `dist/` to any static hosting:
- AWS S3 + CloudFront
- Google Cloud Storage
- Azure Static Web Apps
- GitHub Pages

### Environment Variables (Production)

Set in your hosting platform:
- `VITE_API_BASE_URL` → Your production API URL

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to backend"

**Solution**: Ensure backend is running at `http://localhost:8000`

```bash
cd ..
uvicorn src.main_refactored:app --reload
```

### Issue: CORS errors

**Solution**: Backend CORS is configured to allow all origins. Check backend logs.

### Issue: 401 Unauthorized

**Solution**:
1. Check JWT token in localStorage
2. Re-login
3. Verify backend JWT secret matches

### Issue: Settings not saving

**Solution**: Backend endpoints not implemented yet. Check `BACKEND_CHANGE_REQUEST.md`

---

## 📚 Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router v6** - Routing
- **Zustand** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Radix UI** - Accessible primitives
- **Lucide React** - Icons
- **date-fns** - Date formatting

---

## 📄 License

Private - Internal Use Only

---

## 👥 Team

For questions or support:
- Front-End Lead: [Your Name]
- Backend Team: See `docs/BACKEND_CHANGE_REQUEST.md`
- Slack: #apb-agent-development

---

## 🎯 Roadmap

### Phase 1 (Current - MVP)
- ✅ Authentication
- ✅ Conversational interface
- ✅ Approval flow
- ✅ Settings page
- ⏳ Backend endpoint implementation

### Phase 2 (Investor Demo)
- Multi-thread conversations
- Thread history sidebar
- Advanced calendar visualization
- Rich message formatting
- File attachments

### Phase 3 (Production)
- Real-time updates (WebSockets)
- Push notifications
- Mobile responsive design
- Accessibility audit
- Performance optimization
- E2E testing
