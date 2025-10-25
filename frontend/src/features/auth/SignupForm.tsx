import { useState } from "react";
import { Button } from "@/components/atoms/Button";
import { FormField } from "@/components/molecules/FormField";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/atoms/Card";
import { useAuthStore } from "@/store/useAuthStore";
import { Loader2 } from "lucide-react";

interface SignupFormProps {
  onSuccess: () => void;
}

export function SignupForm({ onSuccess }: SignupFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [internalDomain, setInternalDomain] = useState("");
  const [timezone, setTimezone] = useState("America/Los_Angeles");
  const { signup, isLoading, error } = useAuthStore();
  const [successMessage, setSuccessMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await signup(email, password, internalDomain, timezone);
      setSuccessMessage("Account created successfully! Please sign in.");
      setTimeout(() => {
        onSuccess();
      }, 2000);
    } catch (err) {
      // Error is handled by the store
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Create Account</CardTitle>
        <CardDescription>Sign up for a new Agentic ABP account</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <FormField
            label="Email"
            id="signup-email"
            type="email"
            placeholder="user@company.com"
            value={email}
            onChange={setEmail}
            required
          />

          <FormField
            label="Password"
            id="signup-password"
            type="password"
            placeholder="Create a strong password"
            value={password}
            onChange={setPassword}
            required
          />

          <FormField
            label="Internal Domain"
            id="internal-domain"
            type="text"
            placeholder="company.com"
            value={internalDomain}
            onChange={setInternalDomain}
            required
          />

          <FormField
            label="Timezone"
            id="timezone"
            type="text"
            placeholder="America/Los_Angeles"
            value={timezone}
            onChange={setTimezone}
          />

          {error && (
            <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">
              {error}
            </div>
          )}

          {successMessage && (
            <div className="bg-green-50 text-green-700 text-sm p-3 rounded-md border border-green-200">
              {successMessage}
            </div>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating account...
              </>
            ) : (
              "Create Account"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
