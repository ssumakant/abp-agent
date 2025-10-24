# Changelog

All notable changes to the ABP Agent project will be documented in this file.

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
