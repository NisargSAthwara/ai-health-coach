
import React from 'react';
import { Activity, Target, Droplet, Clock, TrendingUp } from 'lucide-react';

const HealthDashboard = () => {
  const healthMetrics = [
    {
      label: 'Steps Today',
      value: '8,247',
      target: '10,000',
      icon: Activity,
      color: 'emerald',
      progress: 82
    },
    {
      label: 'Water Intake',
      value: '6',
      target: '8 glasses',
      icon: Droplet,
      color: 'blue',
      progress: 75
    },
    {
      label: 'Sleep',
      value: '7.5h',
      target: '8h',
      icon: Clock,
      color: 'purple',
      progress: 94
    },
    {
      label: 'Goals Met',
      value: '3',
      target: '5 daily',
      icon: Target,
      color: 'orange',
      progress: 60
    }
  ];

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
                <span className="text-xs text-gray-500 font-medium">{metric.progress}%</span>
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
                    style={{ width: `${metric.progress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-emerald-200">
        <h3 className="font-semibold text-emerald-900 mb-2">Today's Tip</h3>
        <p className="text-sm text-emerald-700">
          You're doing great! Try to drink 2 more glasses of water to reach your hydration goal. 
          Small consistent steps lead to big health improvements.
        </p>
      </div>
    </div>
  );
};

export default HealthDashboard;
