
import React, { useState } from 'react';
import { Calculator, Scale, Zap, BookOpen, Search, PlusCircle } from 'lucide-react';
import BMICalculator from './calculators/BMICalculator';
import BMRCalculator from './calculators/BMRCalculator';
import WeightLogger from './calculators/WeightLogger';
import NutritionGuide from './calculators/NutritionGuide';
import FoodSearch from './calculators/FoodSearch';
import AddEntry from './calculators/AddEntry';
import { useAuth } from '../context/AuthContext';

type ActiveTool = 'bmi' | 'weight' | 'bmr' | 'nutrition' | 'food' | 'entry' | null;

const QuickActions = () => {
  const [activeTool, setActiveTool] = useState<ActiveTool>(null);
  const { isAuthenticated } = useAuth();

  const actions = [
    {
      id: 'bmi' as const,
      label: 'Calculate BMI',
      description: 'Check your body mass index',
      icon: Calculator,
      color: 'emerald'
    },
    {
      id: 'weight' as const,
      label: 'Log Weight',
      description: 'Track weight changes',
      icon: Scale,
      color: 'blue'
    },
    {
      id: 'bmr' as const,
      label: 'BMR Calculator',
      description: 'Find your metabolic rate',
      icon: Zap,
      color: 'orange'
    },
    {
      id: 'nutrition' as const,
      label: 'Nutrition Guide',
      description: 'Get personalized tips',
      icon: BookOpen,
      color: 'purple'
    },
    {
      id: 'food' as const,
      label: 'Food Search',
      description: 'Find nutrition info',
      icon: Search,
      color: 'teal'
    },
    {
      id: 'entry' as const,
      label: 'Add Entry',
      description: 'Log your activities',
      icon: PlusCircle,
      color: 'indigo',
      requiresAuth: false,
    }
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      emerald: 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200 border-emerald-200',
      blue: 'bg-blue-100 text-blue-700 hover:bg-blue-200 border-blue-200',
      orange: 'bg-orange-100 text-orange-700 hover:bg-orange-200 border-orange-200',
      purple: 'bg-purple-100 text-purple-700 hover:bg-purple-200 border-purple-200',
      teal: 'bg-teal-100 text-teal-700 hover:bg-teal-200 border-teal-200',
      indigo: 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200 border-indigo-200'
    };
    return colors[color as keyof typeof colors] || colors.emerald;
  };

  const renderActiveTool = () => {
    switch (activeTool) {
      case 'bmi':
        return <BMICalculator onBack={() => setActiveTool(null)} />;
      case 'weight':
        return <WeightLogger onBack={() => setActiveTool(null)} />;
      case 'bmr':
        return <BMRCalculator onBack={() => setActiveTool(null)} />;
      case 'nutrition':
        return <NutritionGuide onBack={() => setActiveTool(null)} />;
      case 'food':
        return <FoodSearch onBack={() => setActiveTool(null)} />;
      case 'entry':
        return <AddEntry onBack={() => setActiveTool(null)} />;
      default:
        return null;
    }
  };

  if (activeTool) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {renderActiveTool()}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Quick Actions</h2>
        <p className="text-gray-600">Fast access to health tools and calculators</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <button
              key={action.id}
              onClick={() => setActiveTool(action.id)}
              className={`p-4 rounded-lg border text-left transition-all duration-200 hover:shadow-md hover:scale-105 animate-fade-in ${getColorClasses(action.color)} ${action.requiresAuth && !isAuthenticated ? 'opacity-50 cursor-not-allowed' : ''}`}
              style={{ animationDelay: `${index * 100}ms` }}
              disabled={action.requiresAuth && !isAuthenticated}
            >
              <div className="flex flex-col items-center space-y-3">
                <Icon className="h-8 w-8" />
                <div className="text-center">
                  <h3 className="font-semibold text-sm">{action.label}</h3>
                  <p className="text-xs opacity-75 mt-1">{action.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default QuickActions;
