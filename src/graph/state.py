"""Agent state definition for LangGraph workflow."""
from typing import TypedDict, Optional, List, Dict, Any, Annotated
import operator


class AgentState(TypedDict):
    """State passed between graph nodes."""
    original_request: str
    user_id: str
    user_context: Dict[str, Any]
    intent: Optional[str]
    is_busy: Optional[bool]
    density_percentage: Optional[float]
    busy_message: Optional[str]
    candidate_meetings: Optional[List[Dict[str, Any]]]
    chosen_meeting: Optional[Dict[str, Any]]
    proposed_new_time: Optional[str]
    drafted_email: Optional[Dict[str, Any]]
    requires_approval: bool
    approval_type: Optional[str]
    approval_data: Optional[Dict[str, Any]]
    new_meeting: Optional[Dict[str, Any]]
    final_response: str
    error: Optional[str]
    messages: Annotated[List[Dict[str, str]], operator.add]
