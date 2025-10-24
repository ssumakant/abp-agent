import { useEffect, useState } from "react";
import { Header } from "@/components/layouts/Header";
import { MessageList } from "@/components/organisms/MessageList";
import { ChatInputForm } from "@/components/organisms/ChatInputForm";
import { ApprovalRequestCard } from "@/features/chat/ApprovalRequestCard";
import { DraftEmailReviewModal } from "@/features/chat/DraftEmailReviewModal";
import { useChatStore } from "@/store/useChatStore";

export function ChatPage() {
  const { messages, isLoading, pendingApproval, sendMessage, handleApproval } = useChatStore();
  const [showEmailModal, setShowEmailModal] = useState(false);

  // Check if pending approval is for email review
  useEffect(() => {
    if (pendingApproval?.approvalType === "email_review" && pendingApproval.approvalData.drafted_email) {
      setShowEmailModal(true);
    }
  }, [pendingApproval]);

  const handleSendMessage = (content: string) => {
    sendMessage(content);
  };

  const handleApproveCard = async () => {
    if (pendingApproval?.approvalType === "email_review") {
      setShowEmailModal(true);
    } else {
      await handleApproval(true);
    }
  };

  const handleDenyCard = async () => {
    await handleApproval(false);
  };

  const handleSendEmail = async (editedBody: string) => {
    await handleApproval(true, editedBody);
    setShowEmailModal(false);
  };

  return (
    <div className="h-screen flex flex-col">
      <Header />

      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto p-4">
            <MessageList messages={messages} isLoading={isLoading} />

            {pendingApproval && pendingApproval.approvalType !== "email_review" && (
              <ApprovalRequestCard
                approvalType={pendingApproval.approvalType}
                approvalData={pendingApproval.approvalData}
                onApprove={handleApproveCard}
                onDeny={handleDenyCard}
                isLoading={isLoading}
              />
            )}
          </div>
        </div>

        <div className="border-t">
          <div className="max-w-4xl mx-auto">
            <ChatInputForm onSend={handleSendMessage} disabled={isLoading} />
          </div>
        </div>
      </main>

      {/* Email Review Modal */}
      {pendingApproval?.approvalData.drafted_email && (
        <DraftEmailReviewModal
          isOpen={showEmailModal}
          onClose={() => setShowEmailModal(false)}
          draftedEmail={pendingApproval.approvalData.drafted_email}
          onSend={handleSendEmail}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}
