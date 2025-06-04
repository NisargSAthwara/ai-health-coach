
import React, { useState, useEffect } from 'react';
import { Activity, Target, Droplet, Clock, TrendingUp } from 'lucide-react';

interface SummaryData {
  date: string;
  metrics: {
    total_steps: number;
    avg_sleep_hours: number;
    avg_water_intake: number;
    total_calories_consumed: number;
  };
  goal_progress: {
    calories?: { current: number; target: number; progress: number };
    water?: { current: number; target: number; progress: number };
    sleep?: { current: number; target: number; progress: number };
    steps?: { current: number; target: number; progress: number };
  };
  daily_tip: string;
}

const HealthDashboard = () => {
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        // For now, using a hardcoded user_id. This should ideally come from authentication.
        const userId = "test_user"; 
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/summary?user_id=${userId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: SummaryData = await response.json();
        setSummaryData(data);
      } catch (err) {
        console.error("Error fetching summary data:", err);
        setError("Failed to load health summary.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();
  }, []);

  const healthMetrics = summaryData ? [
    {
      label: 'Steps Today',
      value: summaryData.metrics.total_steps.toLocaleString(),
      target: summaryData.goal_progress.steps?.target.toLocaleString() || 'N/A',
      icon: Activity,
      color: 'emerald',
      progress: summaryData.goal_progress.steps?.progress || 0
    },
    {
      label: 'Water Intake',
      value: summaryData.metrics.avg_water_intake.toLocaleString(),
      target: `${summaryData.goal_progress.water?.target || 'N/A'} glasses`,
      icon: Droplet,
      color: 'blue',
      progress: summaryData.goal_progress.water?.progress || 0
    },
    {
      label: 'Sleep',
      value: `${summaryData.metrics.avg_sleep_hours}h`,
      target: `${summaryData.goal_progress.sleep?.target || 'N/A'}h`,
      icon: Clock,
      color: 'purple',
      progress: summaryData.goal_progress.sleep?.progress || 0
    },
    {
      label: 'Calories Consumed',
      value: summaryData.metrics.total_calories_consumed.toLocaleString(),
      target: `${summaryData.goal_progress.calories?.target || 'N/A'} kcal`,
      icon: Target,
      color: 'orange',
      progress: summaryData.goal_progress.calories?.progress || 0
    }
  ] : [];

  const getColorClasses = (color: string) => {
    const colors = {
      emerald: 'bg-emerald-500',
      blue: 'bg-blue-500',
      purple: 'bg-purple-500',
      orange: 'bg-orange-500'
    };
    return colors[color as keyof typeof colors] || colors.emerald;
  };

  const getIconColor = (color: string) => {
    const colors = {
      emerald: 'text-emerald-600',
      blue: 'text-blue-600',
      purple: 'text-purple-600',
      orange: 'text-orange-600'
    };
    return colors[color as keyof typeof colors] || colors.emerald;
  };

  if (isLoading) {
    return <div className="text-center text-gray-500">Loading health summary...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500">Error: {error}</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Today's Progress</h2>
          <p className="text-gray-600">Track your daily health metrics</p>
        </div>
        <div className="flex items-center space-x-2 text-emerald-600">
          <TrendingUp className="h-5 w-5" />
          <span className="text-sm font-medium">On track</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {healthMetrics.map((metric, index) => {
          const Icon = metric.icon;
          const progressPercentage = Math.max(0, Math.min(100, metric.progress)); // Ensure progress is between 0 and 100
          return (
            <div
              key={index}
              className="bg-gray-50 rounded-lg p-4 border border-gray-100 hover:shadow-md transition-all duration-200"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg ${getIconColor(metric.color)}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-xs text-gray-500 font-medium">{Math.round(progressPercentage)}%</span>
              </div>
              
              <div className="space-y-2">
                <h3 className="font-medium text-gray-900 text-sm">{metric.label}</h3>
                <div className="flex items-baseline space-x-1">
                  <span className="text-2xl font-bold text-gray-900">{metric.value}</span>
                  <span className="text-xs text-gray-500">of {metric.target}</span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${getColorClasses(metric.color)}`}
                    style={{ width: `${progressPercentage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {summaryData?.daily_tip && (
        <div className="mt-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-emerald-200">
          <h3 className="font-semibold text-emerald-900 mb-2">Today's Tip</h3>
          <p className="text-sm text-emerald-700">
            {summaryData.daily_tip}
          </p>
        </div>
      )}
    </div>
  );
};

export default HealthDashboard;
