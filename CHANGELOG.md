# Changelog

All notable changes to the ABP Agent project will be documented in this file.

## [3.1.0] - 2025-10-25

### 🔴 Critical Bug Fixes

1. **Fixed NameError Crash in Agent Endpoints**
   - **Issue**: `/agent/query` and `/agent/approve` crashed with `NameError: name 'graph' is not defined`
   - **Root Cause**: Graph variable was never initialized in these endpoints
   - **Files**: `src/main_refactored.py:243, 351, 409`
   - **Solution**: Added `graph = await initialize_graph(session)` to all agent endpoints
   - **Impact**: Agent endpoints now work correctly without crashing

2. **Fixed Stateful/Stateless Conflict - Human-in-the-Loop Broken**
   - **Issue**: Approval workflows failed because checkpoints were stored in-memory and lost between requests
   - **Root Cause**: Each endpoint call created new graph with fresh `MemorySaver` instance
   - **Files**: `src/graph/graph_refactored.py:5-29, 207-217`
   - **Solution**: Replaced `MemorySaver` with `AsyncSqliteSaver` for persistent checkpointing
   - **Impact**:
     - Checkpoints now persist to `checkpoints.db` file
     - Human-in-the-Loop approval workflow works correctly
     - `/agent/query` → `/agent/approve` flow completes successfully
     - Checkpoints survive server restarts

3. **Made Graph Initialization Async**
   - **Files**: `src/graph/graph_refactored.py:32, 207`
   - **Changed**: `create_agent_graph()` and `initialize_graph()` are now async
   - **Changed**: All endpoints use `await graph.ainvoke()` instead of `graph.invoke()`
   - **Impact**: Proper async/await support throughout the stack

### ✨ New Features

#### Settings/Constitution Management

4. **GET /api/v1/settings - Get User Constitution**
   - **Files**: `src/main_refactored.py:516-583`
   - **Purpose**: Retrieve user's scheduling rules, work hours, and protected time blocks
   - **Authentication**: JWT Bearer token required
   - **Returns**: Default constitution if user hasn't customized settings
   - **Frontend**: Can now display and manage user preferences

5. **POST /api/v1/settings - Update Constitution**
   - **Files**: `src/main_refactored.py:586-682`
   - **Purpose**: Update user's scheduling preferences
   - **Features**: Supports partial updates (only provided fields are updated)
   - **Storage**: Saves to `scheduling_rules` table with rule types (WORK_HOURS, PROTECTED_TIME, GENERAL)
   - **Frontend**: Settings page now functional

#### Google Account Management

6. **GET /api/v1/auth/google/url - OAuth URL Generation**
   - **Files**: `src/main_refactored.py:687-706`
   - **Purpose**: Generate OAuth URL for connecting Google Calendar
   - **Features**: State parameter contains user_id for callback verification
   - **Frontend**: "Connect Calendar" button now works

7. **GET /api/v1/auth/accounts - List Connected Accounts**
   - **Files**: `src/main_refactored.py:709-738`
   - **Purpose**: List all connected Google Calendar accounts for authenticated user
   - **Returns**: account_id, email, status, connected_at, is_primary
   - **Frontend**: Account management page displays all connections

8. **DELETE /api/v1/auth/accounts/{account_id} - Remove Account**
   - **Files**: `src/main_refactored.py:741-774`
   - **Purpose**: Remove connected Google Calendar account
   - **Features**:
     - Revokes OAuth tokens with Google
     - Prevents deletion if it's the only account (returns 400)
     - Cascade deletes account-specific data
   - **Frontend**: Users can disconnect accounts

### 🗄️ Database Schema Changes

9. **Enhanced OAuthToken Model**
   - **Files**: `src/database/models.py:59-78`
   - **New Columns**:
     - `account_email` (String) - Email of connected Google account
     - `status` (String, default="active") - Account health status (active/expired/revoked/error)
     - `connected_at` (DateTime) - When account was connected
     - `is_primary` (Boolean, default=False) - Primary calendar flag
   - **Migration**: Automatic for new deployments; see Migration Guide for existing databases

10. **New Pydantic Schemas**
    - **Files**: `src/schemas.py:27-115`
    - **Added**:
      - Settings, WorkHours, ProtectedTimeBlock, SchedulingRules
      - SettingsUpdateRequest, SettingsUpdateResponse
      - GoogleAuthUrlResponse, ConnectedAccount, ConnectedAccountsResponse
      - AccountDeleteResponse
    - **Impact**: Full type safety for new endpoints

### 🔧 Enhancements

11. **CredentialsManager Account Management Methods**
    - **Files**: `src/auth/credentials_manager.py:167-232`
    - **New Methods**:
      - `list_connected_accounts(user_id)` - List all OAuth tokens for user
      - `revoke_account(user_id, account_id)` - Revoke and delete account
    - **Features**:
      - Prevents deletion of only account
      - Best-effort OAuth revocation with Google
      - Safe database cleanup

### 📚 Documentation

12. **Comprehensive Release Documentation**
    - **Files**: `docs/v3.1.0_RELEASE_NOTES.md`
    - **Includes**:
      - Detailed bug fix explanations
      - API endpoint documentation with examples
      - Database migration guide
      - Testing checklist
      - Deployment instructions
      - Rollback plan

### ⚠️ Breaking Changes

- **Graph Initialization**: `initialize_graph()` is now async - must use `await`
- **Graph Invocation**: Use `await graph.ainvoke()` instead of `graph.invoke()`
- **Checkpoints**: Now stored in `checkpoints.db` file (add to .gitignore)

### 🎯 Frontend Integration Ready

- Frontend can now disable mock data (`VITE_ENABLE_MOCK_API=false`)
- All P0 (critical) endpoints implemented
- Settings and Account Management pages fully functional
- Remove mocks from `frontend/src/services/apiClient.ts`

### 📦 Dependencies

- Requires `langgraph>=0.4.0` for AsyncSqliteSaver support

### 🧪 Testing

- Human-in-the-Loop workflow tested and verified
- All new endpoints tested with JWT authentication
- Checkpoint persistence verified across server restarts
- Multi-user concurrent access tested

---

## [3.0.1] - 2025-10-24

### Fixed

#### Critical Bug Fixes

1. **Fixed NoneType AttributeError in Intent Detection**
   - **Issue**: `'NoneType' object has no attribute 'get'` error when LLM returned null/invalid JSON
   - **Files**: `src/services/llm_service.py:46-50`
   - **Solution**: Added validation after JSON parsing to check if result is None or not a dict, falling back to keyword-based detection
   - **Impact**: Prevents crashes when LLM service returns unexpected responses

2. **Fixed state.get() with None Values**
   - **Issue**: `state.get('new_meeting', {})` returned None instead of default {} when key existed with None value
   - **Files**: `src/graph/nodes_refactored.py:144, 192`
   - **Solution**: Changed from `state.get('new_meeting', {})` to `state.get('new_meeting') or {}`
   - **Impact**: Prevents AttributeError when accessing properties on expected dict

3. **Fixed Duplicate Message Concatenation**
   - **Issue**: Messages appeared duplicated like "No available slots.No available slots."
   - **Files**: `src/graph/state.py:23`
   - **Solution**: Removed `Annotated[str, operator.add]` annotation from final_response field
   - **Impact**: Messages now properly overwrite instead of concatenate

4. **Fixed Silent 404 Calendar Errors**
   - **Issue**: Calendar 404 errors were caught but execution continued with empty data, showing misleading "calendar is busy" messages
   - **Files**: `src/services/calendar_service.py:37-48`
   - **Solution**: Added explicit HttpError handling to detect 404 status and raise CalendarAPIError with clear message
   - **Impact**: Users now see "Google Calendar not found" instead of confusing error messages

#### Enhancements

5. **Added Missing CalendarService Methods**
   - **Issue**: AttributeError when calling `calendar.find_available_slots()` and `calendar.create_event()`
   - **Files**: `src/services/calendar_service.py:70-114`
   - **Added Methods**:
     - `find_available_slots()` - Wrapper around calendar_tools and rescheduling_tools
     - `create_event()` - Wrapper around calendar_tools.create_calendar_event
   - **Impact**: Complete service layer implementation for calendar operations

6. **Improved Error Handling in nodes_refactored.py**
   - **Files**: `src/graph/nodes_refactored.py:93-96`
   - **Added**: Generic Exception handler as safety net for unexpected errors in determine_intent
   - **Impact**: Graceful fallback to 'unknown' intent with user-friendly error message

7. **Better Authentication Error Messages**
   - **Files**: `src/services/calendar_service.py:82-86`
   - **Added**: Explicit credential check with clear error message when Google Calendar not connected
   - **Impact**: Clear guidance to users when OAuth not completed

### Added

8. **Created schemas.py Module**
   - **File**: `src/schemas.py`
   - **Purpose**: Centralize Pydantic models for API requests/responses
   - **Models**:
     - `Token` - Access token response model
     - `UserCreateRequest` - User creation request schema
     - `AgentInvokeRequest` - Agent invocation request schema
     - `TokenData` - JWT token data schema
   - **Impact**: Better type safety and API validation

### Technical Details

#### Files Modified
- `src/services/llm_service.py` - LLM response validation
- `src/graph/nodes_refactored.py` - State handling and error handling
- `src/graph/state.py` - Message concatenation fix
- `src/services/calendar_service.py` - Added methods and error handling
- `src/main_refactored.py` - Safety checks for None response_state

#### Files Created
- `src/schemas.py` - Pydantic models for API

### Testing
- All fixes tested with curl commands against /agent/invoke endpoint
- Verified error messages are user-friendly and actionable
- Confirmed fallback mechanisms work when LLM fails

### Migration Notes
- No breaking changes for API consumers
- Error responses now more descriptive
- OAuth setup still required for calendar access

---

## [3.0.0] - 2025-10-23

### Added
- Initial refactored release with service layer architecture
- LangGraph workflow with human-in-the-loop approvals
- Google Calendar integration
- Google Gemini LLM integration
- JWT authentication
- Constitution-based meeting validation
- Intelligent rescheduling with tiered search logic

---

## Format
- **[Major.Minor.Patch]** - Date
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes
