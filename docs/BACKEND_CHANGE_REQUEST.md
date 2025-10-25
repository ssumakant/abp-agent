# Backend Change Request (CR) for Front-End Support

**Date:** October 24, 2025
**Requested By:** Front-End Team
**Priority:** High (Required for Settings & Account Management UI)
**Status:** Pending Implementation

---

## Executive Summary

To support the full UX/UI Design Specification, the following backend endpoints need to be implemented. These endpoints enable user settings management, Google account connection/management, and proper approval flow support.

---

## 1. Settings/Constitution Management Endpoints

### 1.1 GET /api/v1/settings

**Purpose:** Retrieve the user's scheduling rules and preferences (the "Constitution")

**Authentication:** Required (JWT Bearer token)

**Request:**
```http
GET /api/v1/settings
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "user_id": "string",
  "work_hours": {
    "start": "09:00",
    "end": "17:00",
    "timezone": "America/Los_Angeles"
  },
  "protected_time_blocks": [
    {
      "id": "uuid",
      "name": "Kids School Run",
      "day_of_week": "weekdays",
      "start_time": "15:00",
      "end_time": "16:00",
      "recurring": true
    }
  ],
  "scheduling_rules": {
    "no_weekend_meetings": true,
    "busyness_threshold": 0.85,
    "lookahead_days": 14
  }
}
```

**Status Code:** 200 OK, 401 Unauthorized, 404 Not Found

---

### 1.2 POST /api/v1/settings

**Purpose:** Update the user's scheduling rules and preferences

**Authentication:** Required (JWT Bearer token)

**Request:**
```http
POST /api/v1/settings
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "work_hours": {
    "start": "09:00",
    "end": "17:00"
  },
  "protected_time_blocks": [
    {
      "name": "Kids School Run",
      "day_of_week": "weekdays",
      "start_time": "15:00",
      "end_time": "16:00",
      "recurring": true
    }
  ],
  "scheduling_rules": {
    "no_weekend_meetings": true,
    "busyness_threshold": 0.85
  }
}
```

**Response:**
```json
{
  "message": "Settings updated successfully",
  "updated_at": "2025-10-24T10:30:00Z"
}
```

**Status Code:** 200 OK, 400 Bad Request, 401 Unauthorized

---

## 2. Google Account Management Endpoints

### 2.1 GET /api/v1/auth/google/url

**Purpose:** Generate OAuth URL for connecting a new Google Calendar account

**Authentication:** Required (JWT Bearer token)

**Request:**
```http
GET /api/v1/auth/google/url
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=...&state=<user_id>"
}
```

**Implementation Notes:**
- The `state` parameter should encode the user_id for callback verification
- Scopes should include: `https://www.googleapis.com/auth/calendar` and `https://www.googleapis.com/auth/calendar.events`
- Redirect URI should point to your existing `/auth/callback` endpoint

**Status Code:** 200 OK, 401 Unauthorized

---

### 2.2 GET /api/v1/auth/accounts

**Purpose:** List all connected Google Calendar accounts for the authenticated user

**Authentication:** Required (JWT Bearer token)

**Request:**
```http
GET /api/v1/auth/accounts
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "accounts": [
    {
      "account_id": "uuid",
      "email": "user@company.com",
      "is_primary": true,
      "connected_at": "2025-10-01T12:00:00Z",
      "status": "active"
    },
    {
      "account_id": "uuid-2",
      "email": "personal@gmail.com",
      "is_primary": false,
      "connected_at": "2025-10-15T14:30:00Z",
      "status": "active"
    }
  ]
}
```

**Status Code:** 200 OK, 401 Unauthorized

---

### 2.3 DELETE /api/v1/auth/accounts/{account_id}

**Purpose:** Remove a connected Google Calendar account

**Authentication:** Required (JWT Bearer token)

**Request:**
```http
DELETE /api/v1/auth/accounts/{account_id}
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "Account disconnected successfully",
  "account_id": "uuid"
}
```

**Implementation Notes:**
- Should revoke OAuth tokens for that account
- Should prevent deletion if it's the user's only connected account (return 400 Bad Request)
- Should cascade delete any account-specific data

**Status Code:** 200 OK, 400 Bad Request, 401 Unauthorized, 404 Not Found

---

## 3. Approval Flow Enhancement

### 3.1 Update POST /agent/approve

**Current Implementation:**
```python
class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool
    user_id: str
```

**Required Enhancement:**
```python
class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool
    user_id: str
    edited_email_body: Optional[str] = None  # NEW FIELD
```

**Purpose:** Allow users to edit the drafted email body before the agent sends it

**Implementation Notes:**
- If `edited_email_body` is provided and `approved=True`, use the edited version instead of the original draft
- The edited body should replace the `drafted_email["body"]` in the agent state before execution
- Validation: Email body should have reasonable length limits (e.g., 10-10,000 characters)

**Status:** ✅ **ALREADY IMPLEMENTED** (Updated in this CR)

---

## 4. Thread Management Enhancement

### 4.1 GET /api/v1/threads

**Purpose:** List all conversation threads for the authenticated user (for multi-thread support)

**Authentication:** Required (JWT Bearer token)

**Request:**
```http
GET /api/v1/threads
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "threads": [
    {
      "thread_id": "uuid",
      "title": "Schedule client meetings",
      "last_message": "I've scheduled your meeting with...",
      "created_at": "2025-10-24T09:00:00Z",
      "updated_at": "2025-10-24T10:30:00Z",
      "message_count": 5
    }
  ]
}
```

**Status Code:** 200 OK, 401 Unauthorized

---

### 4.2 POST /api/v1/threads

**Purpose:** Create a new conversation thread

**Authentication:** Required (JWT Bearer token)

**Request:**
```http
POST /api/v1/threads
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "New Conversation"
}
```

**Response:**
```json
{
  "thread_id": "uuid",
  "title": "New Conversation",
  "created_at": "2025-10-24T10:35:00Z"
}
```

**Status Code:** 201 Created, 401 Unauthorized

---

### 4.3 DELETE /api/v1/threads/{thread_id}

**Purpose:** Delete a conversation thread and its history

**Authentication:** Required (JWT Bearer token)

**Request:**
```http
DELETE /api/v1/threads/{thread_id}
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "message": "Thread deleted successfully",
  "thread_id": "uuid"
}
```

**Status Code:** 200 OK, 401 Unauthorized, 404 Not Found

---

## 5. Database Schema Changes Required

### 5.1 New Table: `scheduling_rules`

```sql
CREATE TABLE scheduling_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    rule_type VARCHAR(50) NOT NULL,
    rule_definition JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_user_rule UNIQUE(user_id, rule_type)
);

-- Indexes
CREATE INDEX idx_scheduling_rules_user ON scheduling_rules(user_id);
```

**Initial Data Migration:**
- Populate with `get_default_constitution()` for all existing users

---

### 5.2 Update Table: `oauth_tokens`

Add a `status` column to track account health:

```sql
ALTER TABLE oauth_tokens ADD COLUMN status VARCHAR(20) DEFAULT 'active';
ALTER TABLE oauth_tokens ADD COLUMN connected_at TIMESTAMP DEFAULT NOW();

-- Valid statuses: 'active', 'expired', 'revoked', 'error'
```

---

### 5.3 New Table: `conversation_threads` (Optional for Multi-Thread Support)

```sql
CREATE TABLE conversation_threads (
    thread_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    message_count INT DEFAULT 0
);

CREATE INDEX idx_threads_user ON conversation_threads(user_id);
CREATE INDEX idx_threads_updated ON conversation_threads(updated_at DESC);
```

---

## 6. Implementation Priority

| Priority | Endpoint(s) | Reason |
|----------|-------------|--------|
| **P0 (Critical)** | GET/POST /api/v1/settings | Settings page is core UX feature |
| **P0 (Critical)** | GET /api/v1/auth/accounts | Must show connected accounts |
| **P0 (Critical)** | GET /api/v1/auth/google/url | User needs to connect calendar |
| **P1 (High)** | DELETE /api/v1/auth/accounts | Account management |
| **P1 (High)** | ApprovalRequest.edited_email_body | Already done ✅ |
| **P2 (Medium)** | Thread management endpoints | Nice-to-have for MVP |

---

## 7. Testing Checklist

For each endpoint, ensure:

- ✅ JWT authentication works correctly
- ✅ User can only access their own data (no cross-user leakage)
- ✅ Proper error handling for invalid inputs
- ✅ OAuth token refresh logic works for expired tokens
- ✅ Database transactions are atomic (rollback on failure)
- ✅ Logging for audit trail
- ✅ Rate limiting to prevent abuse

---

## 8. API Documentation

Once implemented, update:
- OpenAPI/Swagger docs at `/docs`
- Postman collection for front-end team testing
- Add examples for each endpoint in README.md

---

## 9. Front-End Mocking Strategy

Until these endpoints are implemented, the front-end will:
1. Use **mock data** in `apiClient.ts` for Settings and Accounts
2. Show a **"Coming Soon"** message when users click "Add New Account"
3. Display **sample connected accounts** in the Settings page
4. Log warnings in console: `"Using mocked endpoint: GET /api/v1/settings"`

---

## 10. Estimated Implementation Time

| Task | Estimate |
|------|----------|
| Settings endpoints (GET/POST) | 2-3 hours |
| Account management endpoints | 2-3 hours |
| Thread management endpoints | 3-4 hours |
| Database migrations | 1-2 hours |
| Testing & documentation | 2-3 hours |
| **Total** | **10-15 hours** |

---

## 11. Contact

For questions or clarifications, contact:
- **Front-End Lead:** [Your Name]
- **Slack Channel:** #apb-agent-development
- **Jira Epic:** ABP-FRONTEND-001

---

**Approval Required From:**
- [ ] Backend Tech Lead
- [ ] Product Manager
- [ ] DevOps (for database migrations)

---

## Appendix: Example Constitution JSON

```json
{
  "protected_times": [
    {
      "name": "Kids School Run",
      "day_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
      "start_time": "15:00",
      "end_time": "16:00",
      "timezone": "America/Los_Angeles"
    }
  ],
  "work_hours": {
    "start": "09:00",
    "end": "17:00",
    "timezone": "America/Los_Angeles"
  },
  "rules": {
    "no_weekend_meetings": true,
    "protect_weekends": true,
    "busy_threshold": 0.85,
    "lookahead_days": 14,
    "minimum_notice_hours": 24
  }
}
```
