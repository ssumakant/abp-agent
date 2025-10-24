import { useEffect } from "react";
import { Button } from "@/components/atoms/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/atoms/Card";
import { useSettingsStore } from "@/store/useSettingsStore";
import { Loader2, Plus, Trash2, CheckCircle2, AlertCircle } from "lucide-react";

export function ConnectedAccountsList() {
  const { connectedAccounts, fetchConnectedAccounts, connectGoogleAccount, removeAccount, isLoading } =
    useSettingsStore();

  useEffect(() => {
    fetchConnectedAccounts();
  }, [fetchConnectedAccounts]);

  const handleConnect = async () => {
    try {
      await connectGoogleAccount();
    } catch (error) {
      // Error is handled by store
    }
  };

  const handleRemove = async (accountId: string) => {
    if (window.confirm("Are you sure you want to disconnect this account?")) {
      await removeAccount(accountId);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Connected Accounts</CardTitle>
        <CardDescription>Manage your Google Calendar connections</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {connectedAccounts.length === 0 && !isLoading && (
          <p className="text-sm text-muted-foreground">No accounts connected yet</p>
        )}

        {connectedAccounts.map((account) => (
          <div
            key={account.account_id}
            className="flex items-center justify-between p-3 border rounded-lg"
          >
            <div className="flex items-center gap-3">
              {account.status === "active" ? (
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              ) : (
                <AlertCircle className="w-5 h-5 text-destructive" />
              )}
              <div>
                <p className="font-medium">{account.email}</p>
                <p className="text-xs text-muted-foreground">
                  {account.is_primary && "Primary • "}
                  Connected {new Date(account.connected_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleRemove(account.account_id)}
              disabled={isLoading}
            >
              <Trash2 className="w-4 h-4 text-destructive" />
            </Button>
          </div>
        ))}

        <Button variant="outline" onClick={handleConnect} className="w-full" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Connecting...
            </>
          ) : (
            <>
              <Plus className="w-4 h-4 mr-2" />
              Add New Account
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
