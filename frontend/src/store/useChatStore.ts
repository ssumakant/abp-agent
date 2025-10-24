/**
 * Chat/Conversation Store
 * Manages conversation state, messages, and approvals using Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import * as api from '@/services/apiClient';
import type { Message, ApprovalData, ApprovalType } from '@/types';

interface ChatState {
  messages: Message[];
  currentThreadId: string | null;
  isLoading: boolean;
  error: string | null;

  // Approval state
  pendingApproval: {
    threadId: string;
    approvalType: ApprovalType;
    approvalData: ApprovalData;
  } | null;

  // Actions
  sendMessage: (content: string) => Promise<void>;
  handleApproval: (approved: boolean, editedEmailBody?: string) => Promise<void>;
  clearMessages: () => void;
  setCurrentThread: (threadId: string | null) => void;
  clearError: () => void;
}

export const useChatStore = create<ChatState>()(
  devtools(
    (set, get) => ({
      messages: [],
      currentThreadId: null,
      isLoading: false,
      error: null,
      pendingApproval: null,

      sendMessage: async (content: string) => {
        const { messages, currentThreadId } = get();

        // Add user message immediately (optimistic update)
        const userMessage: Message = {
          id: `msg-${Date.now()}`,
          role: 'user',
          content,
          timestamp: new Date().toISOString(),
        };

        set({
          messages: [...messages, userMessage],
          isLoading: true,
          error: null,
        });

        try {
          const response = await api.getAgentResponse(content, currentThreadId || undefined);

          const agentMessage: Message = {
            id: `msg-${Date.now()}-agent`,
            role: 'agent',
            content: response.response,
            timestamp: new Date().toISOString(),
            requires_approval: response.requires_approval,
            approval_type: response.approval_type,
            approval_data: response.approval_data,
          };

          set((state) => ({
            messages: [...state.messages, agentMessage],
            currentThreadId: response.thread_id,
            isLoading: false,
            pendingApproval: response.requires_approval
              ? {
                  threadId: response.thread_id,
                  approvalType: response.approval_type!,
                  approvalData: response.approval_data || {},
                }
              : null,
          }));
        } catch (error: any) {
          set({
            error: error.message || 'Failed to send message',
            isLoading: false,
          });

          // Add error message to chat
          const errorMessage: Message = {
            id: `msg-${Date.now()}-error`,
            role: 'agent',
            content: `❌ ${error.message || 'An error occurred'}`,
            timestamp: new Date().toISOString(),
          };

          set((state) => ({
            messages: [...state.messages, errorMessage],
          }));
        }
      },

      handleApproval: async (approved: boolean, editedEmailBody?: string) => {
        const { pendingApproval, messages, currentThreadId } = get();

        if (!pendingApproval || !currentThreadId) {
          console.error('No pending approval or thread ID');
          return;
        }

        set({ isLoading: true, error: null });

        try {
          const response = await api.sendApproval({
            thread_id: pendingApproval.threadId,
            approved,
            user_id: currentThreadId,
            edited_email_body: editedEmailBody,
          });

          const agentMessage: Message = {
            id: `msg-${Date.now()}-approval`,
            role: 'agent',
            content: response.response,
            timestamp: new Date().toISOString(),
          };

          set({
            messages: [...messages, agentMessage],
            isLoading: false,
            pendingApproval: null,
          });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to process approval',
            isLoading: false,
          });
        }
      },

      clearMessages: () => {
        set({
          messages: [],
          currentThreadId: null,
          pendingApproval: null,
        });
      },

      setCurrentThread: (threadId: string | null) => {
        set({ currentThreadId: threadId });
      },

      clearError: () => set({ error: null }),
    }),
    { name: 'ChatStore' }
  )
);
