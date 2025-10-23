"""Application constants."""

# Schedule Analysis
DEFAULT_BUSY_THRESHOLD = 0.85
DEFAULT_WORK_HOURS_START = "09:00"
DEFAULT_WORK_HOURS_END = "17:00"
DEFAULT_LOOKAHEAD_DAYS = 14
BUSYNESS_CALCULATION_DAYS = 7

# Protected Time
KIDS_SCHOOL_RUN_START = "07:30"
KIDS_SCHOOL_RUN_END = "08:30"
PROTECTED_WEEKENDS = ['saturday', 'sunday']

# API Limits
MAX_CALENDAR_EVENTS_PER_REQUEST = 250
CALENDAR_API_TIMEOUT_SECONDS = 30

# LLM Configuration
LLM_MODEL = "gemini-1.5-pro"
LLM_TEMPERATURE = 0
LLM_MAX_TOKENS = 1000

# Intent Types
INTENT_SCHEDULE_MEETING = "schedule_meeting"
INTENT_RESCHEDULE_MEETING = "reschedule_meeting"
INTENT_CHECK_AVAILABILITY = "check_availability"
INTENT_ASSESS_BUSYNESS = "assess_busyness"
INTENT_UNKNOWN = "unknown"

# Messages
MSG_CALENDAR_ACCESS_FAILED = "Unable to access your calendar."
MSG_NO_MEETINGS_FOUND = "No suitable meetings found to reschedule."
MSG_UNEXPECTED_ERROR = "An unexpected error occurred."
