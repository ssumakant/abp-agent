import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/atoms/Card";
import { Button } from "@/components/atoms/Button";
import { AlertTriangle, Calendar, Mail } from "lucide-react";
import type { ApprovalType, ApprovalData } from "@/types";

interface ApprovalRequestCardProps {
  approvalType: ApprovalType;
  approvalData: ApprovalData;
  onApprove: () => void;
  onDeny: () => void;
  isLoading?: boolean;
}

export function ApprovalRequestCard({
  approvalType,
  approvalData,
  onApprove,
  onDeny,
  isLoading,
}: ApprovalRequestCardProps) {
  const getCardConfig = () => {
    switch (approvalType) {
      case "constitution_override":
        return {
          icon: <AlertTriangle className="w-5 h-5 text-destructive" />,
          title: "⚠️ Override Required",
          variant: "destructive" as const,
          bgClass: "bg-red-50 border-red-200",
        };
      case "reschedule_meeting":
        return {
          icon: <Calendar className="w-5 h-5 text-yellow-600" />,
          title: "📅 Approval Needed: Reschedule Meeting",
          variant: "default" as const,
          bgClass: "bg-yellow-50 border-yellow-200",
        };
      case "email_review":
        return {
          icon: <Mail className="w-5 h-5 text-blue-600" />,
          title: "✉️ Review Email Before Sending",
          variant: "default" as const,
          bgClass: "bg-blue-50 border-blue-200",
        };
      default:
        return {
          icon: null,
          title: "❓ Approval Needed",
          variant: "default" as const,
          bgClass: "bg-gray-50 border-gray-200",
        };
    }
  };

  const config = getCardConfig();

  return (
    <Card className={`${config.bgClass} border-2 my-4`}>
      <CardHeader>
        <div className="flex items-center gap-2">
          {config.icon}
          <CardTitle className="text-lg">{config.title}</CardTitle>
        </div>
        <CardDescription>
          {approvalType === "constitution_override" && approvalData.rule_violated && (
            <p className="mt-2">
              The requested action violates your rule: <strong>{approvalData.rule_violated}</strong>
            </p>
          )}
          {approvalType === "reschedule_meeting" && (
            <p className="mt-2">
              {approvalData.suggested_action || "A meeting needs to be rescheduled to accommodate your request."}
            </p>
          )}
        </CardDescription>
      </CardHeader>

      {approvalData && Object.keys(approvalData).length > 0 && (
        <CardContent>
          <div className="space-y-2 text-sm">
            {approvalData.meeting_title && (
              <div>
                <span className="font-medium">Meeting:</span> {approvalData.meeting_title}
              </div>
            )}
            {approvalData.meeting_time && (
              <div>
                <span className="font-medium">Time:</span> {approvalData.meeting_time}
              </div>
            )}
            {approvalData.proposed_new_time && (
              <div>
                <span className="font-medium">New Time:</span> {approvalData.proposed_new_time}
              </div>
            )}
            {approvalData.chosen_meeting && (
              <div className="bg-white p-3 rounded border">
                <p className="font-medium">{approvalData.chosen_meeting.summary}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {new Date(approvalData.chosen_meeting.start.dateTime).toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      )}

      <CardFooter className="flex gap-2">
        <Button onClick={onDeny} variant="outline" disabled={isLoading}>
          Deny / Cancel
        </Button>
        <Button onClick={onApprove} disabled={isLoading}>
          {isLoading ? "Processing..." : "Confirm / Proceed"}
        </Button>
      </CardFooter>
    </Card>
  );
}
