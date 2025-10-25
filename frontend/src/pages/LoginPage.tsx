import { useState } from "react";
import { LoginForm } from "@/features/auth/LoginForm";
import { SignupForm } from "@/features/auth/SignupForm";
import { Button } from "@/components/atoms/Button";

export function LoginPage() {
  const [showSignup, setShowSignup] = useState(false);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md space-y-4">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary text-primary-foreground text-2xl font-bold mb-4">
            A
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Agentic ABP</h1>
          <p className="text-gray-600 mt-2">Your AI-Powered Administrative Business Partner</p>
        </div>

        {showSignup ? (
          <>
            <SignupForm onSuccess={() => setShowSignup(false)} />
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Already have an account?{" "}
                <Button
                  variant="link"
                  className="p-0 h-auto"
                  onClick={() => setShowSignup(false)}
                >
                  Sign in
                </Button>
              </p>
            </div>
          </>
        ) : (
          <>
            <LoginForm />
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Don't have an account?{" "}
                <Button
                  variant="link"
                  className="p-0 h-auto"
                  onClick={() => setShowSignup(true)}
                >
                  Sign up
                </Button>
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
