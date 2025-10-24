"""LLM service - handles LLM interactions."""
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM operations."""
    
    def __init__(self):
        from langchain_google_genai import ChatGoogleGenerativeAI
        from src.config import settings
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            google_api_key=settings.google_api_key
        )
    
    def detect_intent(self, user_request: str, constitution: Dict[str, Any]) -> Dict[str, Any]:
        """Detect user's intent from natural language."""
        from langchain_core.messages import SystemMessage, HumanMessage
        
        system_prompt = f"""You are an executive assistant AI. Determine the user's intent.

Available intents:
- schedule_meeting
- reschedule_meeting  
- check_availability
- assess_busyness
- unknown

Respond with JSON: {{"intent": "intent_name", "entities": {{}}, "confidence": 0.95}}"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_request)
            ])
            if not response or not response.content:
                logger.warning("LLM returned empty response, using fallback")
                return self._fallback_intent_detection(user_request)

            parsed = json.loads(response.content)
            if not parsed or not isinstance(parsed, dict):
                logger.warning(f"LLM returned invalid response: {parsed}, using fallback")
                return self._fallback_intent_detection(user_request)
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"LLM returned invalid JSON: {e}, using fallback")
            return self._fallback_intent_detection(user_request)
        except Exception as e:
            logger.error(f"LLM invoke failed: {e}, using fallback")
            return self._fallback_intent_detection(user_request)
    
    def _fallback_intent_detection(self, request: str) -> Dict[str, Any]:
        """Fallback keyword-based intent detection."""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ['reschedule', 'free up', 'move']):
            intent = 'reschedule_meeting'
        elif any(word in request_lower for word in ['book', 'schedule', 'create']):
            intent = 'schedule_meeting'
        elif any(word in request_lower for word in ['free', 'available', 'when', 'calendar', 'tomorrow', 'today', 'schedule', 'what', 'meetings']):
            intent = 'check_availability'
        elif any(word in request_lower for word in ['busy', 'how is']):
            intent = 'assess_busyness'
        else:
            intent = 'unknown'
        
        return {'intent': intent, 'entities': {}, 'confidence': 0.5}
