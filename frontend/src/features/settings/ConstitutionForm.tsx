import { useState, useEffect } from "react";
import { Button } from "@/components/atoms/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/atoms/Card";
import { Label } from "@/components/atoms/Label";
import { Input } from "@/components/atoms/Input";
import { Switch } from "@/components/atoms/Switch";
import { useSettingsStore } from "@/store/useSettingsStore";
import { Loader2, Plus, Trash2 } from "lucide-react";
import type { Settings, ProtectedTimeBlock } from "@/types";

export function ConstitutionForm() {
  const { settings, updateSettings, isLoading, error } = useSettingsStore();

  const [workHoursStart, setWorkHoursStart] = useState("09:00");
  const [workHoursEnd, setWorkHoursEnd] = useState("17:00");
  const [busynessThreshold, setBusynessThreshold] = useState(0.85);
  const [noWeekendMeetings, setNoWeekendMeetings] = useState(true);
  const [protectedBlocks, setProtectedBlocks] = useState<ProtectedTimeBlock[]>([]);

  useEffect(() => {
    if (settings) {
      setWorkHoursStart(settings.work_hours.start);
      setWorkHoursEnd(settings.work_hours.end);
      setBusynessThreshold(settings.scheduling_rules.busyness_threshold);
      setNoWeekendMeetings(settings.scheduling_rules.no_weekend_meetings);
      setProtectedBlocks(settings.protected_time_blocks);
    }
  }, [settings]);

  const addProtectedBlock = () => {
    setProtectedBlocks([
      ...protectedBlocks,
      {
        name: "",
        day_of_week: "weekdays",
        start_time: "09:00",
        end_time: "10:00",
        recurring: true,
      },
    ]);
  };

  const removeProtectedBlock = (index: number) => {
    setProtectedBlocks(protectedBlocks.filter((_, i) => i !== index));
  };

  const updateProtectedBlock = (index: number, field: keyof ProtectedTimeBlock, value: any) => {
    const updated = [...protectedBlocks];
    updated[index] = { ...updated[index], [field]: value };
    setProtectedBlocks(updated);
  };

  const handleSave = async () => {
    const updatedSettings: Partial<Settings> = {
      work_hours: {
        start: workHoursStart,
        end: workHoursEnd,
        timezone: settings?.work_hours.timezone || "America/Los_Angeles",
      },
      scheduling_rules: {
        no_weekend_meetings: noWeekendMeetings,
        busyness_threshold: busynessThreshold,
        lookahead_days: settings?.scheduling_rules.lookahead_days || 14,
      },
      protected_time_blocks: protectedBlocks,
    };

    try {
      await updateSettings(updatedSettings);
      alert("Settings saved successfully!");
    } catch (err) {
      // Error is handled by store
    }
  };

  return (
    <div className="space-y-6">
      {/* Schedule Density */}
      <Card>
        <CardHeader>
          <CardTitle>Schedule Density</CardTitle>
          <CardDescription>Define your work hours and busyness threshold</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="work-start">Work Hours Start</Label>
              <Input
                id="work-start"
                type="time"
                value={workHoursStart}
                onChange={(e) => setWorkHoursStart(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="work-end">Work Hours End</Label>
              <Input
                id="work-end"
                type="time"
                value={workHoursEnd}
                onChange={(e) => setWorkHoursEnd(e.target.value)}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="threshold">Busyness Threshold: {Math.round(busynessThreshold * 100)}%</Label>
            <Input
              id="threshold"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={busynessThreshold}
              onChange={(e) => setBusynessThreshold(parseFloat(e.target.value))}
              className="mt-2"
            />
            <p className="text-xs text-muted-foreground mt-1">
              The agent will proactively suggest rescheduling when your schedule exceeds this threshold
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Scheduling Rules */}
      <Card>
        <CardHeader>
          <CardTitle>Scheduling Rules</CardTitle>
          <CardDescription>Set your meeting preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Label>No business meetings on weekends</Label>
              <p className="text-sm text-muted-foreground">
                Prevent meetings from being scheduled on Saturdays and Sundays
              </p>
            </div>
            <Switch
              checked={noWeekendMeetings}
              onCheckedChange={setNoWeekendMeetings}
            />
          </div>
        </CardContent>
      </Card>

      {/* Protected Time Blocks */}
      <Card>
        <CardHeader>
          <CardTitle>Protected Time Blocks</CardTitle>
          <CardDescription>Define times when meetings cannot be scheduled</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {protectedBlocks.map((block, index) => (
            <div key={index} className="border rounded-lg p-4 space-y-3">
              <div className="flex justify-between items-start">
                <Input
                  placeholder="Block name (e.g., Kids School Run)"
                  value={block.name}
                  onChange={(e) => updateProtectedBlock(index, "name", e.target.value)}
                  className="flex-1 mr-2"
                />
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeProtectedBlock(index)}
                >
                  <Trash2 className="w-4 h-4 text-destructive" />
                </Button>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label>Start Time</Label>
                  <Input
                    type="time"
                    value={block.start_time}
                    onChange={(e) => updateProtectedBlock(index, "start_time", e.target.value)}
                  />
                </div>
                <div>
                  <Label>End Time</Label>
                  <Input
                    type="time"
                    value={block.end_time}
                    onChange={(e) => updateProtectedBlock(index, "end_time", e.target.value)}
                  />
                </div>
              </div>

              <div>
                <Label>Days</Label>
                <Input
                  placeholder="weekdays, monday, etc."
                  value={block.day_of_week}
                  onChange={(e) => updateProtectedBlock(index, "day_of_week", e.target.value)}
                />
              </div>
            </div>
          ))}

          <Button variant="outline" onClick={addProtectedBlock} className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Add Protected Time Block
          </Button>
        </CardContent>
      </Card>

      {error && (
        <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">
          {error}
        </div>
      )}

      <Button onClick={handleSave} className="w-full" disabled={isLoading}>
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Saving...
          </>
        ) : (
          "Save Changes"
        )}
      </Button>
    </div>
  );
}
