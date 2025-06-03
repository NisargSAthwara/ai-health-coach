
import React, { useState, useEffect } from 'react';
import { BookOpen, ArrowLeft, Lightbulb } from 'lucide-react';

interface NutritionGuideProps {
  onBack: () => void;
}

const NutritionGuide: React.FC<NutritionGuideProps> = ({ onBack }) => {
  const [currentTipIndex, setCurrentTipIndex] = useState(0);

  const nutritionTips = [
    {
      title: "Stay Hydrated",
      content: "Drink at least 8 glasses of water daily. Start your morning with a glass of water to kickstart your metabolism.",
      category: "Hydration",
      color: "blue"
    },
    {
      title: "Portion Control",
      content: "Use smaller plates and bowls to naturally reduce portion sizes. Fill half your plate with vegetables, quarter with protein, and quarter with whole grains.",
      category: "Eating Habits",
      color: "green"
    },
    {
      title: "Protein Power",
      content: "Include protein in every meal to feel fuller longer. Good sources include lean meats, fish, eggs, beans, and nuts.",
      category: "Nutrition",
      color: "purple"
    },
    {
      title: "Quick Workout",
      content: "Take a 10-minute walk after meals to aid digestion and boost energy. Even small movements make a big difference!",
      category: "Exercise",
      color: "orange"
    },
    {
      title: "Mindful Eating",
      content: "Eat slowly and without distractions. It takes 20 minutes for your brain to register fullness.",
      category: "Habits",
      color: "teal"
    },
    {
      title: "Meal Prep",
      content: "Prepare healthy snacks in advance. Cut vegetables, portion nuts, or prepare fruit to avoid unhealthy choices.",
      category: "Planning",
      color: "indigo"
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTipIndex((prev) => (prev + 1) % nutritionTips.length);
    }, 10000); // Change tip every 10 seconds

    return () => clearInterval(timer);
  }, [nutritionTips.length]);

  const currentTip = nutritionTips[currentTipIndex];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'bg-blue-50 border-blue-200 text-blue-700',
      green: 'bg-green-50 border-green-200 text-green-700',
      purple: 'bg-purple-50 border-purple-200 text-purple-700',
      orange: 'bg-orange-50 border-orange-200 text-orange-700',
      teal: 'bg-teal-50 border-teal-200 text-teal-700',
      indigo: 'bg-indigo-50 border-indigo-200 text-indigo-700'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <BookOpen className="h-6 w-6 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">Nutrition Guide</h3>
        </div>
        <button
          onClick={onBack}
          className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
      </div>

      <div className="space-y-6">
        <div className={`p-6 rounded-lg border transition-all duration-500 ${getColorClasses(currentTip.color)}`}>
          <div className="flex items-start space-x-3">
            <Lightbulb className="h-6 w-6 flex-shrink-0 mt-1" />
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <h4 className="font-semibold text-lg">{currentTip.title}</h4>
                <span className="text-xs px-2 py-1 rounded-full bg-white bg-opacity-50">
                  {currentTip.category}
                </span>
              </div>
              <p className="leading-relaxed">{currentTip.content}</p>
            </div>
          </div>
        </div>

        <div className="flex justify-center space-x-2">
          {nutritionTips.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentTipIndex(index)}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index === currentTipIndex ? 'bg-purple-500' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {nutritionTips.slice(0, 4).map((tip, index) => (
            <button
              key={index}
              onClick={() => setCurrentTipIndex(index)}
              className="p-4 text-left rounded-lg border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all duration-200"
            >
              <h5 className="font-medium text-gray-900 mb-1">{tip.title}</h5>
              <p className="text-sm text-gray-600 line-clamp-2">{tip.content}</p>
              <span className="inline-block text-xs text-purple-600 mt-2">{tip.category}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NutritionGuide;
