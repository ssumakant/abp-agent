"""Refactored FastAPI application with service layer."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging

# ... keep your existing imports, and add these:
from datetime import datetime, timedelta
from fastapi import status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.schemas import (
    Token, UserCreateRequest, AgentInvokeRequest, TokenData,
    Settings, SettingsUpdateRequest, SettingsUpdateResponse,
    GoogleAuthUrlResponse, ConnectedAccount, ConnectedAccountsResponse, AccountDeleteResponse,
    WorkHours, ProtectedTimeBlock, SchedulingRules
)  # We importing from the newly created schemas file


from src.config import settings
from src.database import init_db, get_session
from src.database.models import User
from src.graph.graph_refactored import initialize_graph
from src.graph.state import AgentState
from src.tools.constitution_tools import get_default_constitution
from src.exceptions import ABPException
from sqlalchemy import select

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Authentication Utility Functions ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)):
    """
    Decode JWT token to get the current user. This is our security check.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Agentic Administrative Business Partner API v3.0 (Refactored)",
    description="AI-powered executive scheduling assistant with service layer",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AgentRequest(BaseModel):
    """Request to interact with the agent."""
    user_id: str
    prompt: str
    thread_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Response from the agent."""
    user_id: str
    response: str
    thread_id: str
    requires_approval: bool = False
    approval_type: Optional[str] = None
    approval_data: Optional[Dict[str, Any]] = None


class ApprovalRequest(BaseModel):
    """User approval/denial of proposed action."""
    thread_id: str
    approved: bool
    user_id: str
    edited_email_body: Optional[str] = None  # Allow users to edit email before sending


# Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Agentic ABP API v3.0 (Refactored) is running",
        "status": "healthy",
        "version": "3.0.0-refactored",
        "architecture": "service-layer"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "llm": "configured",
            "graph": "initialized"
        }
    }


@app.post("/users", response_model=Dict[str, str])
async def create_user(
    request: UserCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    """Create a new user with default constitution."""
    try:
        result = await session.execute(
            select(User).where(User.email == request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        hashed_password = get_password_hash(request.password) # Add this
        new_user = User(
            email=request.email,
            hashed_password=hashed_password, # Add this
            internal_domain=request.internal_domain,
            timezone=request.timezone
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        logger.info(f"Created user: {new_user.email}")
        
        return {
            "user_id": new_user.user_id,
            "email": new_user.email,
            "message": "User created successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get user details."""
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "internal_domain": user.internal_domain,
        "timezone": user.timezone
    }

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/agent/query", response_model=AgentResponse)
async def agent_query(
    request: AgentRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Main endpoint for interacting with the agent.
    Uses stateful graph with persistent checkpointing for Human-in-the-Loop workflows.
    """
    try:
        # Initialize graph with persistent checkpointer
        graph = await initialize_graph(session)

        # Load user from database
        result = await session.execute(
            select(User).where(User.user_id == request.user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Build user context
        user_context = {
            "user_email": user.email,
            "internal_domain": user.internal_domain,
            "timezone": user.timezone,
            "calendars": [user.email],
            "constitution": get_default_constitution(),
            "user_name": user.email.split('@')[0].title()
        }

        # Create or reuse thread ID
        thread_id = request.thread_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        if not request.thread_id:
            # New conversation - create initial state
            initial_state = AgentState(
                original_request=request.prompt,
                user_id=request.user_id,
                user_context=user_context,
                intent=None,
                is_busy=None,
                density_percentage=None,
                busy_message=None,
                candidate_meetings=None,
                chosen_meeting=None,
                proposed_new_time=None,
                drafted_email=None,
                requires_approval=False,
                approval_type=None,
                approval_data=None,
                new_meeting=None,
                final_response="",
                error=None,
                messages=[]
            )

            logger.info(
                f"Processing new request from user {request.user_id}",
                extra={'user_id': request.user_id}
            )

            # Invoke the agent graph (will save checkpoint if interrupted)
            final_state = await graph.ainvoke(initial_state, config=config)
        else:
            # Continue existing conversation from checkpoint
            logger.info(
                f"Continuing conversation {thread_id}",
                extra={'user_id': request.user_id}
            )
            final_state = await graph.ainvoke(None, config=config)
        
        # Extract response
        response_text = final_state.get(
            "final_response",
            "I encountered an error processing your request."
        )
        
        if final_state.get("error"):
            response_text = f"❌ {final_state['error']}"
        
        logger.info(
            f"Request processed successfully",
            extra={'user_id': request.user_id}
        )
        
        return AgentResponse(
            user_id=request.user_id,
            response=response_text,
            thread_id=thread_id,
            requires_approval=final_state.get("requires_approval", False),
            approval_type=final_state.get("approval_type"),
            approval_data=final_state.get("approval_data")
        )
    
    except HTTPException:
        raise
    except ABPException as e:
        logger.error(f"ABP error: {e.message}", extra={'user_id': request.user_id})
        raise HTTPException(status_code=400, detail=e.to_dict())
    except Exception as e:
        logger.exception("Unexpected error in agent query")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/agent/approve", response_model=AgentResponse)
async def approve_action(
    request: ApprovalRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Handle user approval or denial of a proposed action.
    Resumes execution from persistent checkpoint (saved by /agent/query).
    Implements PRD User Story 5.3 - explicit approval requirement.
    """
    try:
        # Initialize graph with persistent checkpointer
        graph = await initialize_graph(session)

        result = await session.execute(
            select(User).where(User.user_id == request.user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        config = {"configurable": {"thread_id": request.thread_id}}

        if request.approved:
            logger.info(
                f"User approved action for thread {request.thread_id}",
                extra={'user_id': request.user_id}
            )

            # Continue execution from checkpoint (resumes from where /agent/query paused)
            final_state = await graph.ainvoke(None, config=config)
            response_text = final_state.get(
                "final_response",
                "Action completed successfully."
            )
        else:
            logger.info(
                f"User denied action for thread {request.thread_id}",
                extra={'user_id': request.user_id}
            )

            response_text = "Action cancelled by user."
            final_state = {"final_response": response_text}

        return AgentResponse(
            user_id=request.user_id,
            response=response_text,
            thread_id=request.thread_id,
            requires_approval=False
        )

    except Exception as e:
        logger.exception("Approval handling failed")
        raise HTTPException(status_code=500, detail="Approval error")

@app.post("/agent/invoke", response_model=AgentResponse)
async def agent_invoke(
    request: AgentInvokeRequest,
    current_user: User = Depends(get_current_user), # Security is handled here
    session: AsyncSession = Depends(get_session)
):
    """
    Invoke the agent with a user query, now with a fully prepared context.
    Returns full AgentResponse with approval support for front-end.
    This endpoint is stateless - suitable for simple queries that don't need approval.
    For Human-in-the-Loop workflows, use /agent/query + /agent/approve instead.
    """
    try:
        # Build a new graph for each request to ensure a fresh state
        graph = await initialize_graph(session)

        # The user_id is now securely taken from the authenticated user
        user_id = current_user.user_id

        # Create or retrieve thread_id for conversation continuity
        thread_id = request.user_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Assemble the complete user_context, as per Claude's brilliant suggestion
        user_context = {
            "user_email": current_user.email,
            "internal_domain": current_user.internal_domain,
            "timezone": current_user.timezone,
            "calendars": [current_user.email],
            "constitution": get_default_constitution(),
            "user_name": current_user.email.split('@')[0].title()
        }

        # This is the final, correct initialization of the agent's state
        input_data = {
            "original_request": request.query,
            "user_id": user_id,
            "user_context": user_context, # The fully populated context
            "intent": None,
            "is_busy": None,
            "density_percentage": None,
            "busy_message": None,
            "candidate_meetings": [],
            "chosen_meeting": None,
            "proposed_new_time": None,
            "drafted_email": None,
            "requires_approval": False,
            "approval_type": None,
            "approval_data": None,
            "new_meeting": None,
            "final_response": "",
            "error": None,
            "messages": []
        }

        # Invoke the agent's brain
        response_state = await graph.ainvoke(input_data, config=config)

        # Safety check
        if not response_state:
            logger.error("Graph returned None response")
            raise HTTPException(status_code=500, detail="Graph execution failed")

        # Extract response from final_response field
        response_text = response_state.get(
            "final_response",
            "I encountered an error processing your request."
        )

        # Check for errors
        if response_state.get("error"):
            response_text = f"❌ {response_state['error']}"

        # Return full AgentResponse for front-end approval flow support
        return AgentResponse(
            user_id=user_id,
            response=response_text,
            thread_id=thread_id,
            requires_approval=response_state.get("requires_approval", False),
            approval_type=response_state.get("approval_type"),
            approval_data=response_state.get("approval_data")
        )

    except Exception as e:
        logger.error(f"Agent invocation failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/callback")
async def google_auth_callback(
    code: str,
    state: str,
    session: AsyncSession = Depends(get_session)
):
    """Handle OAuth callback from Google."""
    from src.auth.credentials_manager import CredentialsManager

    try:
        user_id = state
        creds_manager = CredentialsManager(session)

        credentials = await creds_manager.exchange_code_for_token(code, user_id)

        logger.info(f"OAuth successful for user {user_id}")

        return {
            "message": "Successfully connected Google Calendar",
            "user_id": user_id
        }

    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail="OAuth failed")


# ==================== Settings/Constitution Endpoints ====================

@app.get("/api/v1/settings", response_model=Settings)
async def get_settings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get user's scheduling rules and preferences (constitution).
    Returns default constitution if user hasn't customized settings yet.
    """
    try:
        from src.database.models import SchedulingRule

        # Fetch all scheduling rules for the user
        result = await session.execute(
            select(SchedulingRule).where(SchedulingRule.user_id == current_user.user_id)
        )
        rules = result.scalars().all()

        # If no rules exist, return default constitution
        if not rules:
            default_const = get_default_constitution()
            return Settings(
                user_id=current_user.user_id,
                work_hours=WorkHours(
                    start=default_const.get("work_hours", {}).get("start", "09:00"),
                    end=default_const.get("work_hours", {}).get("end", "17:00"),
                    timezone=current_user.timezone
                ),
                protected_time_blocks=[
                    ProtectedTimeBlock(**block)
                    for block in default_const.get("protected_times", [])
                ],
                scheduling_rules=SchedulingRules(
                    no_weekend_meetings=default_const.get("rules", {}).get("protect_weekends", True),
                    busyness_threshold=default_const.get("rules", {}).get("busy_threshold", 0.85),
                    lookahead_days=default_const.get("rules", {}).get("lookahead_days", 14)
                )
            )

        # Parse rules from database
        work_hours_rule = next((r for r in rules if r.rule_type == "WORK_HOURS"), None)
        protected_times_rule = next((r for r in rules if r.rule_type == "PROTECTED_TIME"), None)
        general_rules = next((r for r in rules if r.rule_type == "GENERAL"), None)

        work_hours_data = work_hours_rule.rule_definition if work_hours_rule else {"start": "09:00", "end": "17:00"}
        protected_blocks_data = protected_times_rule.rule_definition if protected_times_rule else []
        general_data = general_rules.rule_definition if general_rules else {}

        return Settings(
            user_id=current_user.user_id,
            work_hours=WorkHours(
                start=work_hours_data.get("start", "09:00"),
                end=work_hours_data.get("end", "17:00"),
                timezone=current_user.timezone
            ),
            protected_time_blocks=[
                ProtectedTimeBlock(**block) for block in protected_blocks_data
            ] if isinstance(protected_blocks_data, list) else [],
            scheduling_rules=SchedulingRules(
                no_weekend_meetings=general_data.get("no_weekend_meetings", True),
                busyness_threshold=general_data.get("busyness_threshold", 0.85),
                lookahead_days=general_data.get("lookahead_days", 14)
            )
        )

    except Exception as e:
        logger.exception("Failed to get settings")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/settings", response_model=SettingsUpdateResponse)
async def update_settings(
    settings_update: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Update user's scheduling rules and preferences.
    Supports partial updates - only provided fields will be updated.
    """
    try:
        from src.database.models import SchedulingRule
        import uuid

        # Update work hours if provided
        if settings_update.work_hours:
            result = await session.execute(
                select(SchedulingRule).where(
                    SchedulingRule.user_id == current_user.user_id,
                    SchedulingRule.rule_type == "WORK_HOURS"
                )
            )
            work_hours_rule = result.scalar_one_or_none()

            if work_hours_rule:
                work_hours_rule.rule_definition = {
                    "start": settings_update.work_hours.start,
                    "end": settings_update.work_hours.end
                }
            else:
                new_rule = SchedulingRule(
                    rule_id=str(uuid.uuid4()),
                    user_id=current_user.user_id,
                    rule_type="WORK_HOURS",
                    rule_definition={
                        "start": settings_update.work_hours.start,
                        "end": settings_update.work_hours.end
                    }
                )
                session.add(new_rule)

        # Update protected time blocks if provided
        if settings_update.protected_time_blocks is not None:
            result = await session.execute(
                select(SchedulingRule).where(
                    SchedulingRule.user_id == current_user.user_id,
                    SchedulingRule.rule_type == "PROTECTED_TIME"
                )
            )
            protected_rule = result.scalar_one_or_none()

            blocks_data = [block.model_dump() for block in settings_update.protected_time_blocks]

            if protected_rule:
                protected_rule.rule_definition = blocks_data
            else:
                new_rule = SchedulingRule(
                    rule_id=str(uuid.uuid4()),
                    user_id=current_user.user_id,
                    rule_type="PROTECTED_TIME",
                    rule_definition=blocks_data
                )
                session.add(new_rule)

        # Update general scheduling rules if provided
        if settings_update.scheduling_rules:
            result = await session.execute(
                select(SchedulingRule).where(
                    SchedulingRule.user_id == current_user.user_id,
                    SchedulingRule.rule_type == "GENERAL"
                )
            )
            general_rule = result.scalar_one_or_none()

            rules_data = settings_update.scheduling_rules.model_dump()

            if general_rule:
                general_rule.rule_definition = rules_data
            else:
                new_rule = SchedulingRule(
                    rule_id=str(uuid.uuid4()),
                    user_id=current_user.user_id,
                    rule_type="GENERAL",
                    rule_definition=rules_data
                )
                session.add(new_rule)

        await session.commit()

        return SettingsUpdateResponse(
            message="Settings updated successfully",
            updated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.exception("Failed to update settings")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Google Account Management Endpoints ====================

@app.get("/api/v1/auth/google/url", response_model=GoogleAuthUrlResponse)
async def get_google_auth_url(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Generate OAuth URL for connecting a new Google Calendar account.
    The state parameter contains the user_id for callback verification.
    """
    try:
        from src.auth.credentials_manager import CredentialsManager

        creds_manager = CredentialsManager(session)
        auth_url, state = creds_manager.get_authorization_url(state=current_user.user_id)

        return GoogleAuthUrlResponse(auth_url=auth_url)

    except Exception as e:
        logger.exception("Failed to generate Google auth URL")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/auth/accounts", response_model=ConnectedAccountsResponse)
async def get_connected_accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    List all connected Google Calendar accounts for the authenticated user.
    """
    try:
        from src.auth.credentials_manager import CredentialsManager

        creds_manager = CredentialsManager(session)
        token_records = await creds_manager.list_connected_accounts(current_user.user_id)

        accounts = [
            ConnectedAccount(
                account_id=token.token_id,
                email=token.account_email or current_user.email,
                is_primary=token.is_primary or False,
                connected_at=token.connected_at or datetime.utcnow(),
                status=token.status or "active"
            )
            for token in token_records
        ]

        return ConnectedAccountsResponse(accounts=accounts)

    except Exception as e:
        logger.exception("Failed to list connected accounts")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/auth/accounts/{account_id}", response_model=AccountDeleteResponse)
async def remove_connected_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Remove a connected Google Calendar account.
    Revokes OAuth tokens and deletes from database.
    Cannot delete if it's the user's only connected account.
    """
    try:
        from src.auth.credentials_manager import CredentialsManager

        creds_manager = CredentialsManager(session)

        success = await creds_manager.revoke_account(current_user.user_id, account_id)

        if not success:
            raise HTTPException(status_code=404, detail="Account not found")

        return AccountDeleteResponse(
            message="Account disconnected successfully",
            account_id=account_id
        )

    except ValueError as e:
        # Cannot delete only account
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to remove connected account")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main_refactored:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )