import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/atoms/Dialog";
import { Button } from "@/components/atoms/Button";
import { Label } from "@/components/atoms/Label";
import { Textarea } from "@/components/atoms/Textarea";
import type { DraftedEmail } from "@/types";

interface DraftEmailReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  draftedEmail: DraftedEmail;
  onSend: (editedBody: string) => void;
  isLoading?: boolean;
}

export function DraftEmailReviewModal({
  isOpen,
  onClose,
  draftedEmail,
  onSend,
  isLoading,
}: DraftEmailReviewModalProps) {
  const [emailBody, setEmailBody] = useState(draftedEmail.body);

  const handleSend = () => {
    onSend(emailBody);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Review Reschedule Email</DialogTitle>
          <DialogDescription>
            Review and edit the email before sending
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label>To:</Label>
            <p className="text-sm mt-1 text-muted-foreground">{draftedEmail.to}</p>
          </div>

          <div>
            <Label>Subject:</Label>
            <p className="text-sm mt-1 text-muted-foreground">{draftedEmail.subject}</p>
          </div>

          <div>
            <Label htmlFor="email-body">Body:</Label>
            <Textarea
              id="email-body"
              value={emailBody}
              onChange={(e) => setEmailBody(e.target.value)}
              className="mt-1 min-h-[200px]"
              placeholder="Email body..."
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleSend} disabled={isLoading}>
            {isLoading ? "Sending..." : "Send and Reschedule"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
