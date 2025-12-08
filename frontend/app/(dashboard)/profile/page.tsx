"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useRequireAuth } from "@/lib/hooks/use-auth";

type Gender = "male" | "female" | "other" | "prefer_not_to_say";
type NetWeightGoal = "gain" | "lose" | "maintain";
type StrengthGoal = "overall_health" | "compete" | "personal_milestones" | "bodybuilding" | "powerlifting" | "functional_strength";

interface UserData {
  id: number;
  name: string;
  email: string;
  gender: Gender | null;
  weight_lbs: number | null;
  height_ft: number | null;
  height_in: number | null;
  birthdate: string | null;
  net_weight_goal: NetWeightGoal | null;
  strength_goals: StrengthGoal[] | null;
}

export default function ProfilePage() {
  const user = useRequireAuth();
  const queryClient = useQueryClient();

  const { data: userData, isLoading } = useQuery<UserData>({
    queryKey: ["user", "me"],
    queryFn: async () => {
      const response = await apiClient.get("/user/me/");
      return response.data;
    },
    enabled: !!user,
  });

  const [formData, setFormData] = useState({
    gender: "" as Gender | "",
    weight_lbs: "",
    height_ft: "",
    height_in: "",
    birthdate: "",
    net_weight_goal: "" as NetWeightGoal | "",
    strength_goals: [] as StrengthGoal[],
  });

  const [isSaving, setIsSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Determine if any fields have data (should require edit button to modify)
  const hasAnyData = !!(
    userData?.gender ||
    userData?.weight_lbs ||
    userData?.height_ft ||
    userData?.height_in ||
    userData?.birthdate ||
    userData?.net_weight_goal ||
    (userData?.strength_goals && userData.strength_goals.length > 0)
  );
  
  // If no fields have data, start in edit mode (fields are editable by default)
  // If any field has data, require edit button to be clicked
  useEffect(() => {
    if (userData && !hasAnyData) {
      setIsEditing(true);
    } else if (userData && hasAnyData) {
      setIsEditing(false);
    }
  }, [userData, hasAnyData]);

  useEffect(() => {
    if (userData) {
      setFormData({
        gender: userData.gender || "",
        weight_lbs: userData.weight_lbs?.toString() || "",
        height_ft: userData.height_ft?.toString() || "",
        height_in: userData.height_in?.toString() || "",
        birthdate: userData.birthdate ? userData.birthdate.split("T")[0] : "",
        net_weight_goal: userData.net_weight_goal || "",
        strength_goals: userData.strength_goals || [],
      });
    }
  }, [userData]);

  const updateUserMutation = useMutation({
    mutationFn: async (data: Partial<UserData>) => {
      const response = await apiClient.patch("/user/me", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user", "me"] });
      setSaveMessage({ type: "success", text: "Profile updated successfully!" });
      setIsEditing(false);
      setTimeout(() => setSaveMessage(null), 3000);
    },
    onError: (error: any) => {
      setSaveMessage({
        type: "error",
        text: error?.response?.data?.detail || "Failed to update profile",
      });
      setTimeout(() => setSaveMessage(null), 5000);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveMessage(null);

    try {
      const updateData: any = {};
      
      // Handle gender - send value if selected, null if cleared
      if (formData.gender) {
        updateData.gender = formData.gender;
      } else if (userData?.gender) {
        // If gender was previously set but now cleared, send null
        updateData.gender = null;
      }
      
      // Handle weight - send value if entered, null if cleared
      if (formData.weight_lbs) {
        updateData.weight_lbs = parseFloat(formData.weight_lbs);
      } else if (userData?.weight_lbs) {
        updateData.weight_lbs = null;
      }
      
      // Handle height - send values if entered, null if cleared
      if (formData.height_ft) {
        updateData.height_ft = parseInt(formData.height_ft);
      } else if (userData?.height_ft) {
        updateData.height_ft = null;
      }
      
      if (formData.height_in) {
        updateData.height_in = parseInt(formData.height_in);
      } else if (userData?.height_in) {
        updateData.height_in = null;
      }
      
      // Handle birthdate - send value if entered, null if cleared
      if (formData.birthdate) {
        updateData.birthdate = formData.birthdate;
      } else if (userData?.birthdate) {
        updateData.birthdate = null;
      }
      
      // Handle net_weight_goal
      if (formData.net_weight_goal) {
        updateData.net_weight_goal = formData.net_weight_goal;
      } else if (userData?.net_weight_goal) {
        updateData.net_weight_goal = null;
      }
      
      // Handle strength_goals
      if (formData.strength_goals.length > 0) {
        updateData.strength_goals = formData.strength_goals;
      } else if (userData?.strength_goals && userData.strength_goals.length > 0) {
        updateData.strength_goals = [];
      }

      await updateUserMutation.mutateAsync(updateData);
    } catch (error) {
      console.error("Error updating profile:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemoveBirthdate = () => {
    setFormData({ ...formData, birthdate: "" });
  };

  const handleCancel = () => {
    // Reset form data to original values
    if (userData) {
      setFormData({
        gender: userData.gender || "",
        weight_lbs: userData.weight_lbs?.toString() || "",
        height_ft: userData.height_ft?.toString() || "",
        height_in: userData.height_in?.toString() || "",
        birthdate: userData.birthdate ? userData.birthdate.split("T")[0] : "",
        net_weight_goal: userData.net_weight_goal || "",
        strength_goals: userData.strength_goals || [],
      });
    }
    setIsEditing(false);
    setSaveMessage(null);
  };

  const handleStrengthGoalToggle = (goal: StrengthGoal) => {
    setFormData(prev => {
      const current = prev.strength_goals;
      const isSelected = current.includes(goal);
      return {
        ...prev,
        strength_goals: isSelected 
          ? current.filter(g => g !== goal)
          : [...current, goal]
      };
    });
  };

  const formatDisplayValue = (value: string | number | null | undefined, suffix?: string) => {
    if (value === null || value === undefined || value === "") return "Not set";
    return suffix ? `${value} ${suffix}` : String(value);
  };

  const formatGender = (gender: Gender | null) => {
    if (!gender) return "Not set";
    const map: Record<Gender, string> = {
      male: "Male",
      female: "Female",
      other: "Other",
      prefer_not_to_say: "Prefer not to say",
    };
    return map[gender];
  };

  const formatWeightGoal = (goal: NetWeightGoal | null) => {
    if (!goal) return "Not set";
    const map: Record<NetWeightGoal, string> = {
      gain: "Gain",
      lose: "Lose",
      maintain: "Maintain",
    };
    return map[goal];
  };

  const formatStrengthGoals = (goals: StrengthGoal[] | null) => {
    if (!goals || goals.length === 0) return "Not set";
    const map: Record<StrengthGoal, string> = {
      overall_health: "Overall Health",
      compete: "Compete",
      personal_milestones: "Personal Milestones",
      bodybuilding: "Bodybuilding",
      powerlifting: "Powerlifting",
      functional_strength: "Functional Strength",
    };
    return goals.map(goal => map[goal]).join(", ");
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Not set";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
  };

  if (!user) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 sm:px-0">
        <h1 className="text-3xl font-bold text-neutral-900 mb-6">User Settings</h1>

        <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-xl font-semibold text-neutral-900">Personal Information</h2>
                <div className="h-5 w-5 rounded-full bg-primary-100 flex items-center justify-center cursor-help" title="We use this data to provide personalized program recommendations and track your progress over time.">
                  <span className="text-primary-600 text-xs font-semibold">?</span>
                </div>
              </div>
              <p className="text-xs text-neutral-500 max-w-2xl">
                Used for personalized program recommendations and progress tracking. Not displayed publicly unless you choose to show it.
              </p>
            </div>
            {!isEditing && hasAnyData && (
              <button
                type="button"
                onClick={() => setIsEditing(true)}
                className="btn-secondary text-sm flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
            )}
          </div>

          {saveMessage && (
            <div
              className={`mb-4 p-3 rounded-lg ${
                saveMessage.type === "success"
                  ? "bg-green-50 text-green-800 border border-green-200"
                  : "bg-red-50 text-red-800 border border-red-200"
              }`}
            >
              {saveMessage.text}
            </div>
          )}

          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Gender */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1.5">Gender</label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value as Gender | "" })}
                    className="w-full border border-neutral-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">Select gender...</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                    <option value="prefer_not_to_say">Prefer not to say</option>
                  </select>
                </div>

                {/* Weight */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1.5">Weight</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      value={formData.weight_lbs}
                      onChange={(e) => setFormData({ ...formData, weight_lbs: e.target.value })}
                      placeholder="159"
                      className="flex-1 border border-neutral-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <span className="text-neutral-600 font-medium text-sm min-w-[2.5rem]">lbs</span>
                  </div>
                </div>

                {/* Height */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1.5">Height</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min="0"
                      max="8"
                      value={formData.height_ft}
                      onChange={(e) => setFormData({ ...formData, height_ft: e.target.value })}
                      placeholder="5"
                      className="w-16 border border-neutral-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <span className="text-neutral-600 font-medium text-sm">ft</span>
                    <input
                      type="number"
                      min="0"
                      max="11"
                      value={formData.height_in}
                      onChange={(e) => setFormData({ ...formData, height_in: e.target.value })}
                      placeholder="9"
                      className="w-16 border border-neutral-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <span className="text-neutral-600 font-medium text-sm">in</span>
                  </div>
                </div>

                {/* Birthdate */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1.5">Birthdate</label>
                  <div className="relative">
                    <input
                      type="date"
                      value={formData.birthdate}
                      onChange={(e) => setFormData({ ...formData, birthdate: e.target.value })}
                      max={new Date().toISOString().split("T")[0]}
                      className="w-full border border-neutral-300 rounded-lg px-3 py-2 pr-9 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <div className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none">
                      <svg
                        className="w-4 h-4 text-neutral-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                    </div>
                  </div>
                  {formData.birthdate && (
                    <button
                      type="button"
                      onClick={handleRemoveBirthdate}
                      className="mt-1.5 text-xs text-primary-600 hover:text-primary-700 font-medium"
                    >
                      Remove Date
                    </button>
                  )}
                </div>

                {/* Net Weight Goal */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1.5">Weight Goal</label>
                  <select
                    value={formData.net_weight_goal}
                    onChange={(e) => setFormData({ ...formData, net_weight_goal: e.target.value as NetWeightGoal | "" })}
                    className="w-full border border-neutral-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">Select weight goal...</option>
                    <option value="gain">Gain</option>
                    <option value="lose">Lose</option>
                    <option value="maintain">Maintain</option>
                  </select>
                </div>

                {/* Strength Goals - Multi-select checkboxes */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Strength Goals</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {([
                      { value: "overall_health", label: "Overall Health" },
                      { value: "compete", label: "Compete" },
                      { value: "personal_milestones", label: "Personal Milestones" },
                      { value: "bodybuilding", label: "Bodybuilding" },
                      { value: "powerlifting", label: "Powerlifting" },
                      { value: "functional_strength", label: "Functional Strength" },
                    ] as { value: StrengthGoal; label: string }[]).map((option) => (
                      <label
                        key={option.value}
                        className="flex items-center space-x-2 cursor-pointer p-2 rounded-lg hover:bg-neutral-50 transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={formData.strength_goals.includes(option.value)}
                          onChange={() => handleStrengthGoalToggle(option.value)}
                          className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500 focus:ring-2"
                        />
                        <span className="text-sm text-neutral-700">{option.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end gap-3 pt-4 border-t border-neutral-200 mt-4">
                <button
                  type="button"
                  onClick={handleCancel}
                  disabled={isSaving}
                  className="btn-secondary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSaving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Gender - Read Only */}
              <div>
                <label className="block text-xs font-medium text-neutral-500 mb-1">Gender</label>
                <div className="text-sm text-neutral-900 py-2">
                  {formatGender(userData?.gender || null)}
                </div>
              </div>

              {/* Weight - Read Only */}
              <div>
                <label className="block text-xs font-medium text-neutral-500 mb-1">Weight</label>
                <div className="text-sm text-neutral-900 py-2">
                  {formatDisplayValue(userData?.weight_lbs, "lbs")}
                </div>
              </div>

              {/* Height - Read Only */}
              <div>
                <label className="block text-xs font-medium text-neutral-500 mb-1">Height</label>
                <div className="text-sm text-neutral-900 py-2">
                  {userData?.height_ft && userData?.height_in
                    ? `${userData.height_ft} ft ${userData.height_in} in`
                    : "Not set"}
                </div>
              </div>

              {/* Birthdate - Read Only */}
              <div>
                <label className="block text-xs font-medium text-neutral-500 mb-1">Birthdate</label>
                <div className="text-sm text-neutral-900 py-2">
                  {formatDate(userData?.birthdate || null)}
                </div>
              </div>

              {/* Net Weight Goal - Read Only */}
              <div>
                <label className="block text-xs font-medium text-neutral-500 mb-1">Weight Goal</label>
                <div className="text-sm text-neutral-900 py-2">
                  {formatWeightGoal(userData?.net_weight_goal || null)}
                </div>
              </div>

              {/* Strength Goals - Read Only */}
              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-neutral-500 mb-1">Strength Goals</label>
                <div className="text-sm text-neutral-900 py-2">
                  {formatStrengthGoals(userData?.strength_goals || null)}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

