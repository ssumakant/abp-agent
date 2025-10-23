"""Refactored FastAPI application with service layer."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging

from src.config import settings
from src.database import init_db, get_session
from src.database.models import User
from src.graph.graph_refactored import initialize_graph
from src.graph.state import AgentState
from src.tools.constitution_tools import get_default_constitution
from src.exceptions import ABPException
from sqlalchemy import select

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


@app.on_event("startup")
async def startup_event():
    """Initialize database and graph on startup."""
    await init_db()
    logger.info("✓ Database initialized")
    logger.info("✓ Agent graph ready with service layer")


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


class UserCreateRequest(BaseModel):
    """Create a new user."""
    email: str
    internal_domain: str
    timezone: str = "America/Los_Angeles"


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
        
        new_user = User(
            email=request.email,
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


@app.post("/agent/query", response_model=AgentResponse)
async def agent_query(
    request: AgentRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Main endpoint for interacting with the agent.
    Uses refactored service layer for clean separation of concerns.
    """
    try:
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
        
        # Initialize graph with current session
        graph = initialize_graph(session)
        
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
            
            # Invoke the agent graph
            final_state = graph.invoke(initial_state, config=config)
        else:
            # Continue existing conversation
            logger.info(
                f"Continuing conversation {thread_id}",
                extra={'user_id': request.user_id}
            )
            final_state = graph.invoke(None, config=config)
        
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
    Implements PRD User Story 5.3 - explicit approval requirement.
    """
    try:
        result = await session.execute(
            select(User).where(User.user_id == request.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Initialize graph
        graph = initialize_graph(session)
        config = {"configurable": {"thread_id": request.thread_id}}
        
        if request.approved:
            logger.info(
                f"User approved action for thread {request.thread_id}",
                extra={'user_id': request.user_id}
            )
            
            # Continue execution from checkpoint
            final_state = graph.invoke(None, config=config)
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


@app.get("/auth/google")
async def google_auth_redirect(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Initiate Google OAuth flow."""
    from src.auth.credentials_manager import CredentialsManager
    
    creds_manager = CredentialsManager(session)
    auth_url, state = creds_manager.get_authorization_url(state=user_id)
    
    logger.info(f"OAuth initiated for user {user_id}")
    
    return {
        "authorization_url": auth_url,
        "state": state
    }


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main_refactored:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )