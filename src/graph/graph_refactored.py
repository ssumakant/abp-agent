"""
Refactored LangGraph workflow with dependency injection.
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from sqlalchemy.ext.asyncio import AsyncSession

from src.graph.state import AgentState
from src.graph import nodes_refactored as nodes
from src.services.calendar_service import CalendarService
from src.services.rescheduling_service import ReschedulingService
from src.services.llm_service import LLMService
from src.services.email_service import EmailService
from src.auth.credentials_manager import CredentialsManager

# Module-level persistent checkpointer
_checkpointer = None


async def get_checkpointer():
    """
    Get or create the persistent checkpointer.
    Uses AsyncSqliteSaver to persist checkpoints across requests.
    This enables Human-in-the-Loop workflows with /agent/query + /agent/approve.
    """
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = AsyncSqliteSaver.from_conn_string("checkpoints.db")
    return _checkpointer


async def create_agent_graph(session: AsyncSession):
    """
    Create the complete agent workflow graph with dependency injection.

    Args:
        session: Database session for credentials management

    Returns:
        Compiled LangGraph application
    """
    # Initialize services
    creds_manager = CredentialsManager(session)
    calendar_service = CalendarService(creds_manager)
    rescheduling_service = ReschedulingService(calendar_service)
    llm_service = LLMService()
    email_service = EmailService(llm_service, creds_manager)
    
    # Create dependency injection context
    context = nodes.NodeContext(
        calendar_service=calendar_service,
        rescheduling_service=rescheduling_service,
        llm_service=llm_service,
        email_service=email_service
    )
    
    # Inject into nodes
    nodes.set_node_context(context)
    
    # Build workflow
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("load_context", nodes.load_user_context)
    workflow.add_node("determine_intent", nodes.determine_intent)
    workflow.add_node("assess_busyness", nodes.assess_schedule_busyness)
    workflow.add_node("check_constitution", nodes.check_meeting_against_constitution)
    workflow.add_node("find_and_book", nodes.find_and_book_slot)
    workflow.add_node("identify_meetings", nodes.identify_meetings_to_reschedule)
    workflow.add_node("draft_email", nodes.draft_reschedule_email_node)
    workflow.add_node("execute_reschedule", nodes.execute_reschedule)
    workflow.add_node("handle_unknown", nodes.handle_unknown_intent)
    workflow.add_node("return_response", nodes.return_response)
    
    # Set entry point
    workflow.set_entry_point("load_context")
    
    # Build edges
    workflow.add_edge("load_context", "determine_intent")
    
    # Route after intent determination
    workflow.add_conditional_edges(
        "determine_intent",
        _route_after_intent,
        {
            "assess_busyness": "assess_busyness",
            "identify_meetings": "identify_meetings",
            "handle_unknown": "handle_unknown"
        }
    )
    
    # Route after busyness check
    workflow.add_conditional_edges(
        "assess_busyness",
        _route_after_busyness_check,
        {
            "identify_meetings": "identify_meetings",
            "check_constitution": "check_constitution",
            "return_response": "return_response"
        }
    )
    
    # Route after constitution check
    workflow.add_conditional_edges(
        "check_constitution",
        _route_after_constitution_check,
        {
            "find_and_book": "find_and_book",
            "return_response": "return_response"
        }
    )
    
    # Simple edges
    workflow.add_edge("find_and_book", "return_response")
    
    workflow.add_conditional_edges(
        "identify_meetings",
        _route_after_identify_meetings,
        {
            "draft_email": "draft_email",
            "return_response": "return_response"
        }
    )
    
    workflow.add_edge("draft_email", "return_response")
    workflow.add_edge("execute_reschedule", "return_response")
    workflow.add_edge("handle_unknown", "return_response")
    workflow.add_edge("return_response", END)

    # Add persistence with persistent checkpoint (AsyncSqliteSaver)
    # This ensures checkpoints survive across HTTP requests for Human-in-the-Loop
    checkpointer = await get_checkpointer()

    # Compile with human-in-the-loop interrupts
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute_reschedule"]
    )

    return app


# Conditional routing functions
def _route_after_intent(state: AgentState) -> str:
    """Route based on determined intent."""
    from src.configuration.constants import (
        INTENT_SCHEDULE_MEETING,
        INTENT_RESCHEDULE_MEETING,
        INTENT_CHECK_AVAILABILITY,
        INTENT_ASSESS_BUSYNESS
    )
    
    intent = state.get('intent', 'unknown')
    
    if intent == INTENT_SCHEDULE_MEETING:
        return "assess_busyness"
    elif intent == INTENT_RESCHEDULE_MEETING:
        return "identify_meetings"
    elif intent in [INTENT_CHECK_AVAILABILITY, INTENT_ASSESS_BUSYNESS]:
        return "assess_busyness"
    else:
        return "handle_unknown"


def _route_after_busyness_check(state: AgentState) -> str:
    """Route after busyness assessment."""
    from src.configuration.constants import (
        INTENT_ASSESS_BUSYNESS,
        INTENT_CHECK_AVAILABILITY,
        INTENT_SCHEDULE_MEETING
    )
    
    intent = state.get('intent')
    
    if intent in [INTENT_ASSESS_BUSYNESS, INTENT_CHECK_AVAILABILITY]:
        return "return_response"
    
    if intent == INTENT_SCHEDULE_MEETING:
        if state.get('is_busy', False):
            return "identify_meetings"
        else:
            return "check_constitution"
    
    return "return_response"


def _route_after_constitution_check(state: AgentState) -> str:
    """Route after constitution validation."""
    if state.get('requires_approval', False):
        return "return_response"
    else:
        return "find_and_book"


def _route_after_identify_meetings(state: AgentState) -> str:
    """Route after identifying meetings to reschedule."""
    if state.get('chosen_meeting'):
        return "draft_email"
    else:
        return "return_response"


# Create singleton instance
agent_graph = None


async def initialize_graph(session: AsyncSession):
    """
    Initialize the graph with a database session.

    Note: This creates a new graph instance but uses a shared persistent
    checkpointer, allowing Human-in-the-Loop workflows to work correctly
    across multiple HTTP requests.
    """
    global agent_graph
    agent_graph = await create_agent_graph(session)
    return agent_graph