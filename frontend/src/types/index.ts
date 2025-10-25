// API Response Types
export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserCreateRequest {
  email: string;
  password: string;
  internal_domain: string;
  timezone?: string;
}

export interface UserCreateResponse {
  user_id: string;
  email: string;
  message: string;
}

export interface AgentResponse {
  user_id: string;
  response: string;
  thread_id: string;
  requires_approval: boolean;
  approval_type?: ApprovalType;
  approval_data?: ApprovalData;
}

export interface ApprovalRequest {
  thread_id: string;
  approved: boolean;
  user_id: string;
  edited_email_body?: string;
}

// Approval Types
export type ApprovalType =
  | 'constitution_override'
  | 'reschedule_meeting'
  | 'email_review'
  | 'general';

export interface ApprovalData {
  meeting_title?: string;
  meeting_time?: string;
  rule_violated?: string;
  suggested_action?: string;
  drafted_email?: DraftedEmail;
  chosen_meeting?: Meeting;
  proposed_new_time?: string;
  [key: string]: any;
}

export interface DraftedEmail {
  to: string;
  subject: string;
  body: string;
}

export interface Meeting {
  id: string;
  summary: string;
  start: { dateTime: string; timeZone: string };
  end: { dateTime: string; timeZone: string };
  attendees?: Array<{ email: string; responseStatus?: string }>;
  organizer?: { email: string };
}

// Settings Types
export interface Settings {
  user_id: string;
  work_hours: WorkHours;
  protected_time_blocks: ProtectedTimeBlock[];
  scheduling_rules: SchedulingRules;
}

export interface WorkHours {
  start: string;
  end: string;
  timezone: string;
}

export interface ProtectedTimeBlock {
  id?: string;
  name: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  recurring: boolean;
}

export interface SchedulingRules {
  no_weekend_meetings: boolean;
  busyness_threshold: number;
  lookahead_days: number;
}

// Google Account Types
export interface GoogleAccount {
  account_id: string;
  email: string;
  is_primary: boolean;
  connected_at: string;
  status: 'active' | 'expired' | 'error';
}

export interface GoogleAuthUrlResponse {
  auth_url: string;
}

export interface ConnectedAccountsResponse {
  accounts: GoogleAccount[];
}

// Thread/Conversation Types
export interface Thread {
  thread_id: string;
  title: string;
  last_message: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ThreadsResponse {
  threads: Thread[];
}

export interface CreateThreadRequest {
  title: string;
}

// Message Types
export interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
  requires_approval?: boolean;
  approval_type?: ApprovalType;
  approval_data?: ApprovalData;
}

// UI State Types
export interface ConversationState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  currentThreadId: string | null;
}

// API Error Types
export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}
