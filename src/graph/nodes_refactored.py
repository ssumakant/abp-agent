"""
Refactored graph nodes - pure workflow orchestration.
Each node has a SINGLE RESPONSIBILITY and delegates to services.
"""
from typing import Optional
import logging

from src.graph.state import AgentState
from src.services.calendar_service import CalendarService
from src.services.rescheduling_service import ReschedulingService
from src.services.llm_service import LLMService
from src.services.email_service import EmailService
from src.tools.constitution_tools import check_constitution, check_density_threshold
from src.exceptions import (
    CalendarAPIError,
    AuthenticationError,
    ConstitutionViolation,
    LLMError,
    ReschedulingError
)
from src.configuration.constants import (
    MSG_CALENDAR_ACCESS_FAILED,
    MSG_NO_MEETINGS_FOUND,
    MSG_UNEXPECTED_ERROR,
    INTENT_ASSESS_BUSYNESS,
    INTENT_CHECK_AVAILABILITY,
    INTENT_SCHEDULE_MEETING
)

logger = logging.getLogger(__name__)


class NodeContext:
    """Dependency injection container for services."""
    
    def __init__(
        self,
        calendar_service: CalendarService,
        rescheduling_service: ReschedulingService,
        llm_service: LLMService,
        email_service: EmailService
    ):
        self.calendar = calendar_service
        self.rescheduling = rescheduling_service
        self.llm = llm_service
        self.email = email_service


# Global context (initialized in graph.py)
_context: Optional[NodeContext] = None


def set_node_context(context: NodeContext):
    """Set the dependency injection context."""
    global _context
    _context = context


def load_user_context(state: AgentState) -> AgentState:
    """Load user context. In production, queries database."""
    return state


def determine_intent(state: AgentState) -> AgentState:
    """
    Determine user intent using LLM.
    SINGLE RESPONSIBILITY: Intent detection only.
    """
    user_id = state['user_id']
    
    try:
        result = _context.llm.detect_intent(
            user_request=state['original_request'],
            constitution=state['user_context']['constitution']
        )
        
        state['intent'] = result.get('intent', 'unknown') if result else 'unknown'
        
        if result and result.get('entities'):
            state['new_meeting'] = result['entities']
        
        state['messages'].append({
            'role': 'assistant',
            'content': f"Intent: {state['intent']}"
        })
        
        logger.info(f"Intent determined: {state['intent']}", extra={'user_id': user_id})

    except LLMError as e:
        logger.error(f"Intent detection failed: {e.message}", extra={'user_id': user_id})
        state['intent'] = 'unknown'
        state['error'] = "Could not understand your request. Please try rephrasing."
    except Exception as e:
        logger.error(f"Unexpected error in intent detection: {e}", extra={'user_id': user_id})
        state['intent'] = 'unknown'
        state['error'] = "Could not understand your request. Please try rephrasing."

    return state


async def assess_schedule_busyness(state: AgentState) -> AgentState:
    """
    Calculate schedule density.
    SINGLE RESPONSIBILITY: Busyness assessment only.
    """
    user_id = state['user_id']
    user_context = state['user_context']
    
    try:
        busyness = await _context.calendar.calculate_schedule_density(
            user_id=user_id,
            calendar_ids=user_context['calendars'],
            work_hours=user_context['constitution']['working_hours']
        )
        
        state['is_busy'] = busyness['is_busy']
        state['density_percentage'] = busyness['density']
        state['busy_message'] = busyness['message']
        
        if state['intent'] in [INTENT_ASSESS_BUSYNESS, INTENT_CHECK_AVAILABILITY]:
            state['final_response'] = busyness['message']
        
        logger.info(
            f"Schedule density: {busyness['density']*100:.0f}%",
            extra={'user_id': user_id}
        )
        
    except (CalendarAPIError, AuthenticationError) as e:
        logger.error(f"Busyness assessment failed: {e.message}", extra={'user_id': user_id})
        state['error'] = MSG_CALENDAR_ACCESS_FAILED
    except Exception as e:
        logger.exception("Unexpected error in busyness assessment")
        state['error'] = MSG_UNEXPECTED_ERROR
    
    return state


def check_meeting_against_constitution(state: AgentState) -> AgentState:
    """
    Validate proposed meeting against constitution.
    SINGLE RESPONSIBILITY: Rule enforcement only.
    """
    user_id = state['user_id']
    meeting = state.get('new_meeting') or {}
    constitution = state['user_context']['constitution']

    proposed_time = meeting.get('proposed_time') if meeting else None
    if not proposed_time:
        state['requires_approval'] = False
        return state
    
    try:
        meeting_type = meeting.get('meeting_type', 'business')
        
        is_allowed, reason, approval_type = check_constitution(
            meeting_time_str=proposed_time,
            constitution=constitution,
            meeting_type=meeting_type
        )
        
        if not is_allowed:
            state['requires_approval'] = True
            state['approval_type'] = approval_type
            state['approval_data'] = {
                'meeting': meeting,
                'reason': reason,
                'proposed_time': proposed_time
            }
            state['final_response'] = f"⚠️ Override Required: {reason}\n\nWould you like to proceed anyway?"
            
            logger.info(
                f"Constitution violation: {approval_type}",
                extra={'user_id': user_id}
            )
        else:
            state['requires_approval'] = False
            logger.info("Meeting complies with constitution", extra={'user_id': user_id})
        
    except Exception as e:
        logger.exception("Constitution check failed")
        state['error'] = "Unable to validate meeting time"
    
    return state


async def find_and_book_slot(state: AgentState) -> AgentState:
    """
    Find available slot and book meeting.
    SINGLE RESPONSIBILITY: Slot finding and booking only.
    """
    user_id = state['user_id']
    meeting = state.get('new_meeting') or {}
    user_context = state['user_context']
    constitution = user_context['constitution']
    
    try:
        available_slots = await _context.calendar.find_available_slots(
            user_id=user_id,
            calendar_ids=user_context['calendars'],
            duration_minutes=meeting.get('duration', 60),
            work_hours=constitution['working_hours']
        )
        
        if not available_slots:
            state['final_response'] = "No available time slots found. Your calendar is very busy."
            return state
        
        slot = available_slots[0]
        
        is_allowed, reason, approval_type = check_constitution(
            slot['start'],
            constitution
        )
        
        if not is_allowed:
            state['requires_approval'] = True
            state['approval_type'] = approval_type
            state['approval_data'] = {
                'meeting': meeting,
                'reason': reason,
                'proposed_time': slot['start']
            }
            state['final_response'] = f"Found a slot at {slot['start']}, but it requires override: {reason}"
        else:
            created_event = await _context.calendar.create_event(
                user_id=user_id,
                calendar_id='primary',
                summary=meeting.get('title', 'New Meeting'),
                start_time=slot['start'],
                end_time=slot['end'],
                attendees=meeting.get('attendees', []),
                description=meeting.get('description', '')
            )
            
            state['final_response'] = f"✓ Meeting '{meeting.get('title')}' scheduled for {slot['start']}"
            logger.info("Meeting booked successfully", extra={'user_id': user_id})
        
    except (CalendarAPIError, AuthenticationError) as e:
        logger.error(f"Booking failed: {e.message}", extra={'user_id': user_id})
        state['error'] = MSG_CALENDAR_ACCESS_FAILED
    except Exception as e:
        logger.exception("Unexpected error in booking")
        state['error'] = MSG_UNEXPECTED_ERROR
    
    return state


async def identify_meetings_to_reschedule(state: AgentState) -> AgentState:
    """
    Find best meeting to reschedule.
    SINGLE RESPONSIBILITY: Candidate identification only.
    """
    user_id = state['user_id']
    user_context = state['user_context']
    
    try:
        result = await _context.rescheduling.find_best_meeting_to_move(
            user_id=user_id,
            user_email=user_context['user_email'],
            internal_domain=user_context['internal_domain'],
            calendar_ids=user_context['calendars']
        )
        
        if result:
            state['chosen_meeting'] = result['candidate_event']
            state['candidate_meetings'] = [result['candidate_event']]
            state['requires_approval'] = True
            state['approval_type'] = 'reschedule_meeting'
            state['approval_data'] = {
                'meeting': result['candidate_event'],
                'reason': result['explanation']
            }
            
            state['final_response'] = _context.rescheduling.format_reschedule_proposal(result)
            
            logger.info("Rescheduling candidate identified", extra={'user_id': user_id})
        else:
            state['final_response'] = MSG_NO_MEETINGS_FOUND
            logger.info("No rescheduling candidates found", extra={'user_id': user_id})
        
    except (CalendarAPIError, AuthenticationError) as e:
        logger.error(f"Meeting identification failed: {e.message}", extra={'user_id': user_id})
        state['error'] = MSG_CALENDAR_ACCESS_FAILED
    except ReschedulingError as e:
        logger.error(f"Rescheduling error: {e.message}", extra={'user_id': user_id})
        state['error'] = "Unable to identify meetings for rescheduling"
    except Exception as e:
        logger.exception("Unexpected error in meeting identification")
        state['error'] = MSG_UNEXPECTED_ERROR
    
    return state


async def draft_reschedule_email_node(state: AgentState) -> AgentState:
    """
    Draft rescheduling email for approval.
    SINGLE RESPONSIBILITY: Email drafting only.
    """
    user_id = state['user_id']
    meeting = state.get('chosen_meeting')
    
    if not meeting:
        state['error'] = "No meeting selected for rescheduling"
        return state
    
    try:
        available_slots = await _context.calendar.find_available_slots(
            user_id=user_id,
            calendar_ids=state['user_context']['calendars'],
            duration_minutes=60,
            work_hours=state['user_context']['constitution']['working_hours']
        )
        
        if not available_slots:
            state['final_response'] = "No available slots found for rescheduling"
            return state
        
        new_slot = available_slots[0]
        user_name = state['user_context'].get('user_name', 'the organizer')
        
        drafted = _context.email.draft_reschedule_email(
            meeting=meeting,
            new_time_slot=new_slot,
            user_name=user_name
        )
        
        state['drafted_email'] = drafted
        state['proposed_new_time'] = new_slot['start']
        state['requires_approval'] = True
        state['approval_type'] = 'email_approval'
        
        state['final_response'] = f"""📧 **Draft Email for Review**

**To:** {', '.join(drafted['recipients'])}
**Subject:** {drafted['subject']}

**Body:**
{drafted['body']}

Would you like to send this email and reschedule the meeting?"""
        
        logger.info("Email drafted for approval", extra={'user_id': user_id})
        
    except Exception as e:
        logger.exception("Email drafting failed")
        state['error'] = "Unable to draft rescheduling email"
    
    return state


async def execute_reschedule(state: AgentState) -> AgentState:
    """
    Execute approved rescheduling.
    SINGLE RESPONSIBILITY: Execute reschedule and send email.
    """
    user_id = state['user_id']
    drafted_email = state.get('drafted_email')
    
    if not drafted_email:
        state['error'] = "No draft email found"
        return state
    
    try:
        await _context.rescheduling.execute_reschedule(
            user_id=user_id,
            meeting=state['chosen_meeting'],
            new_start_time=drafted_email['new_start'],
            new_end_time=drafted_email['new_end']
        )
        
        await _context.email.send_email(
            user_id=user_id,
            from_address=state['user_context']['user_email'],
            to_addresses=drafted_email['recipients'],
            subject=drafted_email['subject'],
            body=drafted_email['body']
        )
        
        state['final_response'] = "✓ Meeting rescheduled and email sent successfully!"
        logger.info("Reschedule executed successfully", extra={'user_id': user_id})
        
    except Exception as e:
        logger.exception("Failed to execute reschedule")
        state['error'] = "Unable to complete rescheduling"
    
    return state


def handle_unknown_intent(state: AgentState) -> AgentState:
    """Handle requests with unknown intent."""
    state['final_response'] = (
        "I'm sorry, I don't understand that request. I can help you with:\n"
        "- Scheduling meetings\n"
        "- Checking your availability\n"
        "- Rescheduling meetings\n"
        "- Assessing how busy you are"
    )
    return state


def return_response(state: AgentState) -> AgentState:
    """
    Final node to format response.
    SINGLE RESPONSIBILITY: Response formatting only.
    """
    if state.get('error'):
        state['final_response'] = f"❌ {state['error']}"
    
    if not state.get('final_response'):
        state['final_response'] = "Request processed."
    
    return state