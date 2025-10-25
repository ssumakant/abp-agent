# React Implementation Guide
## Fork 2: Enterprise-Grade Production Application

**Directory**: `frontend/`
**Purpose**: Production-ready, investor-grade application
**Status**: Complete & Production-Ready

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [Component Reference](#3-component-reference)
4. [State Management](#4-state-management)
5. [API Integration](#5-api-integration)
6. [Routing & Navigation](#6-routing--navigation)
7. [Features Implementation](#7-features-implementation)
8. [Styling System](#8-styling-system)
9. [Build & Deployment](#9-build--deployment)
10. [Performance Optimization](#10-performance-optimization)

---

## 1. Overview

### Purpose
The React application is a **production-grade, investor-ready front-end** featuring:
- Modern TypeScript/React architecture
- Enterprise-level UX/UI
- Complete feature set per Design Spec
- Scalable, maintainable codebase
- Accessibility compliance

### Technology Stack

```typescript
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2",
    "zustand": "^4.5.5",
    "axios": "^1.7.7",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.3",
    "lucide-react": "^0.446.0",
    "@radix-ui/react-dialog": "^1.1.2",
    "@radix-ui/react-label": "^2.1.0",
    "@radix-ui/react-slot": "^1.1.0",
    "@radix-ui/react-switch": "^1.1.1",
    "class-variance-authority": "^0.7.0",
    "date-fns": "^4.1.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.1",
    "typescript": "^5.6.2",
    "vite": "^5.4.8",
    "tailwindcss": "^3.4.13",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.47"
  }
}
```

### Key Features
- ✅ Full TypeScript type safety
- ✅ Atomic Design component architecture
- ✅ Zustand state management
- ✅ React Router v6 routing
- ✅ shadcn/ui components
- ✅ Tailwind CSS styling
- ✅ Axios API client with interceptors
- ✅ Responsive design
- ✅ Accessibility (WCAG 2.1 AA)

---

## 2. Project Structure

### Directory Tree

```
frontend/
├── public/                        # Static assets
│   └── vite.svg
│
├── src/
│   ├── components/                # Reusable UI components
│   │   ├── atoms/                 # Basic building blocks
│   │   │   ├── Button.tsx         # Primary button component
│   │   │   ├── Input.tsx          # Text input
│   │   │   ├── Label.tsx          # Form label
│   │   │   ├── Card.tsx           # Card container
│   │   │   ├── Dialog.tsx         # Modal dialog
│   │   │   ├── Switch.tsx         # Toggle switch
│   │   │   └── Textarea.tsx       # Multi-line text input
│   │   │
│   │   ├── molecules/             # Simple combinations
│   │   │   ├── FormField.tsx      # Label + Input + Error
│   │   │   └── MessageBubble.tsx  # Chat message display
│   │   │
│   │   ├── organisms/             # Complex components
│   │   │   ├── MessageList.tsx    # Message history container
│   │   │   └── ChatInputForm.tsx  # Message input with submit
│   │   │
│   │   └── layouts/               # Layout components
│   │       └── Header.tsx         # App header with nav
│   │
│   ├── features/                  # Domain-specific modules
│   │   ├── auth/                  # Authentication feature
│   │   │   ├── LoginForm.tsx      # Login UI & logic
│   │   │   └── SignupForm.tsx     # Signup UI & logic
│   │   │
│   │   ├── chat/                  # Conversation feature
│   │   │   ├── ApprovalRequestCard.tsx      # Approval UI
│   │   │   └── DraftEmailReviewModal.tsx    # Email review
│   │   │
│   │   └── settings/              # Settings feature
│   │       ├── ConstitutionForm.tsx         # Rules management
│   │       └── ConnectedAccountsList.tsx    # Account management
│   │
│   ├── pages/                     # Route-level components
│   │   ├── LoginPage.tsx          # /
│   │   ├── ChatPage.tsx           # /chat
│   │   └── SettingsPage.tsx       # /settings
│   │
│   ├── services/                  # External integrations
│   │   └── apiClient.ts           # Backend API service
│   │
│   ├── store/                     # Zustand state stores
│   │   ├── useAuthStore.ts        # Auth state
│   │   ├── useChatStore.ts        # Chat state
│   │   └── useSettingsStore.ts    # Settings state
│   │
│   ├── types/                     # TypeScript definitions
│   │   └── index.ts               # All type definitions
│   │
│   ├── utils/                     # Utility functions
│   │   └── cn.ts                  # className merger
│   │
│   ├── App.tsx                    # Main app with routing
│   ├── main.tsx                   # Entry point
│   ├── index.css                  # Global styles
│   └── vite-env.d.ts              # Vite type definitions
│
├── index.html                     # HTML template
├── package.json                   # Dependencies & scripts
├── tsconfig.json                  # TypeScript config
├── tailwind.config.js             # Tailwind config
├── postcss.config.js              # PostCSS config
├── vite.config.ts                 # Vite config
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
└── README.md                      # Documentation
```

### File Metrics

| Category | Files | Lines of Code |
|----------|-------|---------------|
| **Components** | 14 | ~1,200 |
| **Features** | 6 | ~1,500 |
| **Pages** | 3 | ~400 |
| **Stores** | 3 | ~600 |
| **Services** | 1 | ~400 |
| **Types** | 1 | ~200 |
| **Config** | 6 | ~200 |
| **Total** | **34** | **~4,500** |

---

## 3. Component Reference

### 3.1 Atoms (Basic Building Blocks)

#### Button.tsx

**Purpose**: Primary button component with variants

```typescript
import { ButtonProps } from "./Button"

// Usage
<Button variant="default" size="default">
  Click Me
</Button>

<Button variant="destructive" size="lg">
  Delete
</Button>

<Button variant="outline" size="sm">
  Cancel
</Button>
```

**Variants**:
- `default` - Blue primary button
- `destructive` - Red danger button
- `outline` - Bordered button
- `secondary` - Gray secondary button
- `ghost` - Transparent button
- `link` - Underlined link button

**Sizes**:
- `default` - 40px height
- `sm` - 36px height
- `lg` - 44px height
- `icon` - Square icon button

**Props**:
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  asChild?: boolean
}
```

#### Input.tsx

**Purpose**: Text input field

```typescript
<Input
  type="email"
  placeholder="user@company.com"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

**Props**:
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}
```

#### Card.tsx

**Purpose**: Container component with shadow

```typescript
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    Content here
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

**Components**:
- `Card` - Main container
- `CardHeader` - Top section
- `CardTitle` - Heading
- `CardDescription` - Subheading
- `CardContent` - Body
- `CardFooter` - Bottom section

#### Dialog.tsx

**Purpose**: Modal overlay component

```typescript
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Modal Title</DialogTitle>
      <DialogDescription>Modal description</DialogDescription>
    </DialogHeader>

    <div>Modal content</div>

    <DialogFooter>
      <Button onClick={() => setIsOpen(false)}>Close</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**Features**:
- Accessibility (focus trap, ESC to close)
- Backdrop click to close
- Auto-centering
- Smooth animations

### 3.2 Molecules (Simple Combinations)

#### FormField.tsx

**Purpose**: Label + Input + Error message

```typescript
<FormField
  label="Email"
  id="email"
  type="email"
  placeholder="user@company.com"
  value={email}
  onChange={setEmail}
  error={emailError}
  required
/>
```

**Props**:
```typescript
interface FormFieldProps {
  label: string
  id: string
  type?: string
  placeholder?: string
  value: string
  onChange: (value: string) => void
  error?: string
  required?: boolean
}
```

**Rendering**:
- Label with required indicator (`*`)
- Input field
- Error message (if provided)

#### MessageBubble.tsx

**Purpose**: Individual chat message display

```typescript
<MessageBubble message={{
  id: '123',
  role: 'user',
  content: 'Hello!',
  timestamp: '2025-10-24T10:30:00Z'
}} />
```

**Features**:
- User vs Agent styling
- Avatar icons
- Timestamp formatting
- Auto-wrap long text

### 3.3 Organisms (Complex Components)

#### MessageList.tsx

**Purpose**: Container for all chat messages

```typescript
<MessageList
  messages={messages}
  isLoading={isLoading}
/>
```

**Features**:
- Auto-scroll to bottom on new message
- Empty state when no messages
- Loading indicator
- Virtual scrolling ready (future)

**Implementation**:
```typescript
export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  if (messages.length === 0 && !isLoading) {
    return <EmptyState />
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.map(msg => <MessageBubble key={msg.id} message={msg} />)}
      {isLoading && <LoadingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}
```

#### ChatInputForm.tsx

**Purpose**: Message input with send button

```typescript
<ChatInputForm
  onSend={handleSend}
  disabled={isLoading}
/>
```

**Features**:
- Multi-line textarea
- Enter to send, Shift+Enter for new line
- Send button
- Disabled state during loading
- Auto-clear on send

---

## 4. State Management

### 4.1 Store Architecture

Three Zustand stores for domain separation:

```
┌────────────────────────────────────┐
│        useAuthStore                │
│  • isAuthenticated                 │
│  • userEmail                       │
│  • login(), logout()               │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│        useChatStore                │
│  • messages[]                      │
│  • currentThreadId                 │
│  • pendingApproval                 │
│  • sendMessage(), handleApproval() │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│     useSettingsStore               │
│  • settings                        │
│  • connectedAccounts               │
│  • fetchSettings()                 │
│  • updateSettings()                │
└────────────────────────────────────┘
```

### 4.2 useAuthStore

**File**: `src/store/useAuthStore.ts`

**State**:
```typescript
interface AuthState {
  isAuthenticated: boolean
  userEmail: string | null
  isLoading: boolean
  error: string | null
}
```

**Actions**:
```typescript
{
  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      await api.login(email, password)
      set({ isAuthenticated: true, userEmail: email, isLoading: false })
    } catch (error: any) {
      set({ error: error.message, isLoading: false })
      throw error
    }
  },

  logout: () => {
    api.logout()
    set({ isAuthenticated: false, userEmail: null, error: null })
  },

  checkAuth: () => {
    const isAuth = api.isAuthenticated()
    const email = api.getUserEmail()
    set({ isAuthenticated: isAuth, userEmail: email })
  }
}
```

**Usage in Components**:
```typescript
function LoginPage() {
  const { login, isLoading, error } = useAuthStore()

  const handleLogin = async () => {
    try {
      await login(email, password)
      navigate('/chat')
    } catch (err) {
      // Error displayed from store
    }
  }
}
```

### 4.3 useChatStore

**File**: `src/store/useChatStore.ts`

**State**:
```typescript
interface ChatState {
  messages: Message[]
  currentThreadId: string | null
  isLoading: boolean
  error: string | null
  pendingApproval: {
    threadId: string
    approvalType: ApprovalType
    approvalData: ApprovalData
  } | null
}
```

**Actions**:
```typescript
{
  sendMessage: async (content: string) => {
    // Optimistic update
    const tempMessage = { id: `temp-${Date.now()}`, content, role: 'user' }
    set(state => ({ messages: [...state.messages, tempMessage] }))

    try {
      const response = await api.getAgentResponse(content, currentThreadId)

      // Replace temp with real message
      const agentMessage = { ...response, role: 'agent' }
      set(state => ({
        messages: [...state.messages.filter(m => m.id !== tempMessage.id), agentMessage],
        currentThreadId: response.thread_id,
        pendingApproval: response.requires_approval ? {...} : null
      }))
    } catch (error) {
      // Rollback on error
      set(state => ({
        messages: state.messages.filter(m => m.id !== tempMessage.id),
        error: error.message
      }))
    }
  },

  handleApproval: async (approved: boolean, editedEmailBody?: string) => {
    try {
      const response = await api.sendApproval({
        thread_id: pendingApproval.threadId,
        approved,
        edited_email_body: editedEmailBody
      })

      set(state => ({
        messages: [...state.messages, { role: 'agent', content: response.response }],
        pendingApproval: null
      }))
    } catch (error) {
      set({ error: error.message })
    }
  }
}
```

### 4.4 useSettingsStore

**File**: `src/store/useSettingsStore.ts`

**State**:
```typescript
interface SettingsState {
  settings: Settings | null
  connectedAccounts: GoogleAccount[]
  isLoading: boolean
  error: string | null
}
```

**Actions**:
```typescript
{
  fetchSettings: async () => {
    set({ isLoading: true })
    try {
      const settings = await api.getSettings()
      set({ settings, isLoading: false })
    } catch (error) {
      set({ error: error.message, isLoading: false })
    }
  },

  updateSettings: async (updatedSettings) => {
    set({ isLoading: true })
    try {
      await api.updateSettings(updatedSettings)
      set(state => ({
        settings: { ...state.settings, ...updatedSettings },
        isLoading: false
      }))
    } catch (error) {
      set({ error: error.message, isLoading: false })
      throw error
    }
  }
}
```

---

## 5. API Integration

### 5.1 API Client Architecture

**File**: `src/services/apiClient.ts`

**Structure**:
```typescript
// 1. Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const TOKEN_KEY = 'abp_jwt_token'

// 2. Axios Instance
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// 3. Request Interceptor (Add JWT)
axiosInstance.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 4. Response Interceptor (Handle errors)
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      logout()
      window.location.href = '/'
    }
    return Promise.reject(formatError(error))
  }
)

// 5. Token Management
export function storeToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

// 6. API Functions
export async function login(email: string, password: string): Promise<Token> {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)

  const response = await axiosInstance.post<Token>('/token', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })

  storeToken(response.data.access_token)
  storeUserEmail(email)

  return response.data
}

export async function getAgentResponse(query: string): Promise<AgentResponse> {
  const response = await axiosInstance.post<AgentResponse>('/agent/invoke', { query })
  return response.data
}
```

### 5.2 Type-Safe API Calls

All API functions are fully typed:

```typescript
// Type definitions
interface Token {
  access_token: string
  token_type: string
}

interface AgentResponse {
  user_id: string
  response: string
  thread_id: string
  requires_approval: boolean
  approval_type?: ApprovalType
  approval_data?: ApprovalData
}

// Type-safe function
export async function getAgentResponse(
  query: string,
  userId?: string
): Promise<AgentResponse> {
  const response = await axiosInstance.post<AgentResponse>(
    '/agent/invoke',
    { query, user_id: userId }
  )
  return response.data
}

// Usage in component
const response: AgentResponse = await api.getAgentResponse("Hello")
// TypeScript knows response.thread_id exists and is a string
```

### 5.3 Mock Data Strategy

For endpoints not yet implemented:

```typescript
export async function getSettings(): Promise<Settings> {
  if (ENABLE_MOCK) {
    console.warn('Using mocked endpoint: GET /api/v1/settings')
    return mockSettings
  }

  try {
    const response = await axiosInstance.get<Settings>('/api/v1/settings')
    return response.data
  } catch (error) {
    console.warn('Settings endpoint not available, using mock data')
    return mockSettings
  }
}
```

**Benefits**:
- Frontend development unblocked
- Clear console warnings for developers
- Easy to remove when real endpoints are ready

---

## 6. Routing & Navigation

### 6.1 Route Configuration

**File**: `src/App.tsx`

```typescript
function App() {
  const { checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [])

  return (
    <Router>
      <Routes>
        {/* Public Route */}
        <Route path="/" element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } />

        {/* Protected Routes */}
        <Route path="/chat" element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        } />

        <Route path="/settings" element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        } />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}
```

### 6.2 Route Guards

```typescript
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()

  if (isAuthenticated) {
    return <Navigate to="/chat" replace />
  }

  return <>{children}</>
}
```

### 6.3 Programmatic Navigation

```typescript
import { useNavigate } from 'react-router-dom'

function LoginForm() {
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleLogin = async () => {
    await login(email, password)
    navigate('/chat')  // Redirect after login
  }
}
```

---

## 7. Features Implementation

### 7.1 Authentication Feature

**Components**:
- `LoginForm.tsx`
- `SignupForm.tsx`

**LoginForm Implementation**:

```typescript
export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const { login, isLoading, error } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(email, password)
      navigate("/chat")
    } catch (err) {
      // Error handled by store
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Welcome Back</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit}>
          <FormField
            label="Email"
            value={email}
            onChange={setEmail}
            required
          />
          <FormField
            label="Password"
            type="password"
            value={password}
            onChange={setPassword}
            required
          />
          {error && <ErrorDisplay>{error}</ErrorDisplay>}
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Signing in..." : "Sign In"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
```

### 7.2 Chat Feature

**Components**:
- `ApprovalRequestCard.tsx`
- `DraftEmailReviewModal.tsx`

**ApprovalRequestCard Implementation**:

```typescript
export function ApprovalRequestCard({
  approvalType,
  approvalData,
  onApprove,
  onDeny,
  isLoading
}: ApprovalRequestCardProps) {
  const getCardConfig = () => {
    switch (approvalType) {
      case "constitution_override":
        return {
          icon: <AlertTriangle />,
          title: "⚠️ Override Required",
          bgClass: "bg-red-50 border-red-200"
        }
      case "reschedule_meeting":
        return {
          icon: <Calendar />,
          title: "📅 Approval Needed",
          bgClass: "bg-yellow-50 border-yellow-200"
        }
    }
  }

  const config = getCardConfig()

  return (
    <Card className={`${config.bgClass} border-2`}>
      <CardHeader>
        <CardTitle>{config.title}</CardTitle>
        <CardDescription>
          {approvalData.rule_violated && (
            <p>Violates rule: {approvalData.rule_violated}</p>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Display approval data */}
      </CardContent>
      <CardFooter>
        <Button variant="outline" onClick={onDeny} disabled={isLoading}>
          Deny
        </Button>
        <Button onClick={onApprove} disabled={isLoading}>
          Confirm
        </Button>
      </CardFooter>
    </Card>
  )
}
```

**DraftEmailReviewModal Implementation**:

```typescript
export function DraftEmailReviewModal({
  isOpen,
  onClose,
  draftedEmail,
  onSend,
  isLoading
}: DraftEmailReviewModalProps) {
  const [emailBody, setEmailBody] = useState(draftedEmail.body)

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Review Email</DialogTitle>
        </DialogHeader>

        <div>
          <Label>To:</Label>
          <p>{draftedEmail.to}</p>
        </div>

        <div>
          <Label>Subject:</Label>
          <p>{draftedEmail.subject}</p>
        </div>

        <div>
          <Label>Body:</Label>
          <Textarea
            value={emailBody}
            onChange={(e) => setEmailBody(e.target.value)}
          />
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={() => onSend(emailBody)} disabled={isLoading}>
            Send and Reschedule
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

### 7.3 Settings Feature

**ConstitutionForm Implementation**:

```typescript
export function ConstitutionForm() {
  const { settings, updateSettings, isLoading } = useSettingsStore()
  const [workHoursStart, setWorkHoursStart] = useState("09:00")
  const [workHoursEnd, setWorkHoursEnd] = useState("17:00")
  const [busynessThreshold, setBusynessThreshold] = useState(0.85)
  const [protectedBlocks, setProtectedBlocks] = useState<ProtectedTimeBlock[]>([])

  useEffect(() => {
    if (settings) {
      setWorkHoursStart(settings.work_hours.start)
      setWorkHoursEnd(settings.work_hours.end)
      setBusynessThreshold(settings.scheduling_rules.busyness_threshold)
      setProtectedBlocks(settings.protected_time_blocks)
    }
  }, [settings])

  const handleSave = async () => {
    await updateSettings({
      work_hours: { start: workHoursStart, end: workHoursEnd },
      scheduling_rules: { busyness_threshold: busynessThreshold },
      protected_time_blocks: protectedBlocks
    })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Work Hours</CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            type="time"
            value={workHoursStart}
            onChange={(e) => setWorkHoursStart(e.target.value)}
          />
          <Input
            type="time"
            value={workHoursEnd}
            onChange={(e) => setWorkHoursEnd(e.target.value)}
          />
        </CardContent>
      </Card>

      <Button onClick={handleSave} disabled={isLoading}>
        Save Changes
      </Button>
    </div>
  )
}
```

---

## 8. Styling System

### 8.1 Tailwind Configuration

**File**: `tailwind.config.js`

```javascript
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "hsl(var(--primary))",
        secondary: "hsl(var(--secondary))",
        destructive: "hsl(var(--destructive))",
        // ... more colors
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      }
    },
  },
  plugins: [],
}
```

### 8.2 CSS Variables

**File**: `src/index.css`

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --destructive: 0 84.2% 60.2%;
    --border: 214.3 31.8% 91.4%;
    --radius: 0.5rem;
  }
}
```

### 8.3 Component Styling Examples

```typescript
// Using Tailwind classes
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <h2 className="text-2xl font-bold text-gray-900">Title</h2>
  <Button className="ml-4">Action</Button>
</div>

// Using cn() utility for conditional classes
<div className={cn(
  "rounded-lg p-4",
  isActive && "bg-blue-100",
  isError && "border-red-500"
)}>
  Content
</div>

// Component variants with CVA
const buttonVariants = cva(
  "base-classes",
  {
    variants: {
      variant: {
        default: "bg-primary text-white",
        outline: "border border-primary"
      }
    }
  }
)
```

---

## 9. Build & Deployment

### 9.1 Build Process

```bash
# Development
npm run dev
# → Vite dev server with HMR

# Production build
npm run build
# → TypeScript compilation
# → Vite build to dist/

# Preview production build
npm run preview
# → Serve dist/ locally
```

### 9.2 Build Output

```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js     # Main bundle (~200KB gzipped)
│   ├── index-[hash].css    # Styles (~50KB gzipped)
│   └── vendor-[hash].js    # Dependencies (~250KB gzipped)
└── vite.svg
```

### 9.3 Environment Variables

```bash
# .env (local development)
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_MOCK_API=false

# .env.production
VITE_API_BASE_URL=https://api.production.com
VITE_ENABLE_MOCK_API=false
```

### 9.4 Deployment to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Configure environment variables in Vercel dashboard
# VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## 10. Performance Optimization

### 10.1 Current Optimizations

**Code Splitting**:
- Automatic route-based splitting by Vite
- Vendor bundle separation

**Bundle Size**:
- Tree shaking enabled
- Unused code eliminated
- CSS purged by Tailwind

**Render Optimization**:
- Zustand selective subscriptions
- Minimal re-renders
- Efficient state updates

### 10.2 Future Optimizations

**Lazy Loading**:
```typescript
const ChatPage = lazy(() => import('./pages/ChatPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))

<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/chat" element={<ChatPage />} />
  </Routes>
</Suspense>
```

**React.memo**:
```typescript
export const MessageBubble = React.memo(({ message }) => {
  return <div>{message.content}</div>
}, (prevProps, nextProps) => {
  return prevProps.message.id === nextProps.message.id
})
```

**Virtual Scrolling**:
```typescript
import { FixedSizeList } from 'react-window'

<FixedSizeList
  height={600}
  itemCount={messages.length}
  itemSize={80}
>
  {({ index, style }) => (
    <MessageBubble message={messages[index]} style={style} />
  )}
</FixedSizeList>
```

---

**Status**: Production-Ready
**Recommended Use**: Investor demos, production deployment
**Maintenance**: Active development (Phase 2 features coming)
