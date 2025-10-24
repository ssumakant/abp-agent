import { useEffect } from "react";
import { Header } from "@/components/layouts/Header";
import { Button } from "@/components/atoms/Button";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ConnectedAccountsList } from "@/features/settings/ConnectedAccountsList";
import { ConstitutionForm } from "@/features/settings/ConstitutionForm";
import { useSettingsStore } from "@/store/useSettingsStore";

export function SettingsPage() {
  const navigate = useNavigate();
  const { fetchSettings } = useSettingsStore();

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />

      <main className="flex-1">
        <div className="max-w-4xl mx-auto p-6 space-y-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate("/chat")}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold">The Constitution</h1>
              <p className="text-muted-foreground">
                Define the rules that govern your agent's scheduling behavior
              </p>
            </div>
          </div>

          <ConnectedAccountsList />

          <ConstitutionForm />
        </div>
      </main>
    </div>
  );
}
