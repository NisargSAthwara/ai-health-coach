
import React, { useState } from 'react';
import { Search, ArrowLeft, Camera, Upload } from 'lucide-react';

interface FoodSearchProps {
  onBack: () => void;
}

interface FoodInfo {
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
}

const FoodSearch: React.FC<FoodSearchProps> = ({ onBack }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [foodInfo, setFoodInfo] = useState<FoodInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Mock food database
  const mockFoodDatabase: { [key: string]: FoodInfo } = {
    'apple': { name: 'Apple (medium)', calories: 95, protein: 0.5, carbs: 25, fat: 0.3, fiber: 4 },
    'banana': { name: 'Banana (medium)', calories: 105, protein: 1.3, carbs: 27, fat: 0.4, fiber: 3 },
    'chicken breast': { name: 'Chicken Breast (100g)', calories: 165, protein: 31, carbs: 0, fat: 3.6, fiber: 0 },
    'rice': { name: 'White Rice (1 cup)', calories: 205, protein: 4.3, carbs: 45, fat: 0.4, fiber: 0.6 },
    'broccoli': { name: 'Broccoli (1 cup)', calories: 25, protein: 3, carbs: 5, fat: 0.3, fiber: 2 }
  };

  const searchFood = () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const normalizedQuery = searchQuery.toLowerCase();
      const found = mockFoodDatabase[normalizedQuery];
      
      if (found) {
        setFoodInfo(found);
      } else {
        setFoodInfo({
          name: searchQuery,
          calories: 0,
          protein: 0,
          carbs: 0,
          fat: 0,
          fiber: 0
        });
      }
      setIsLoading(false);
    }, 1000);
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Mock OCR processing
      setIsLoading(true);
      setTimeout(() => {
        setSearchQuery('apple'); // Mock OCR result
        setFoodInfo(mockFoodDatabase['apple']);
        setIsLoading(false);
      }, 2000);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Search className="h-6 w-6 text-teal-600" />
          <h3 className="text-lg font-semibold text-gray-900">Food Search</h3>
        </div>
        <button
          onClick={onBack}
          className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
      </div>

      <div className="space-y-4">
        <div className="flex space-x-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
            placeholder="Search for food (e.g., apple, chicken breast)"
            onKeyPress={(e) => e.key === 'Enter' && searchFood()}
          />
          <button
            onClick={searchFood}
            disabled={!searchQuery.trim() || isLoading}
            className="bg-teal-500 text-white px-4 py-2 rounded-md hover:bg-teal-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Search
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex-1 border-t border-gray-300"></div>
          <span className="text-sm text-gray-500">or</span>
          <div className="flex-1 border-t border-gray-300"></div>
        </div>

        <div className="flex space-x-3">
          <label className="flex-1 flex items-center justify-center px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-teal-400 cursor-pointer transition-colors">
            <Camera className="h-5 w-5 text-gray-500 mr-2" />
            <span className="text-gray-600">Take Photo</span>
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleImageUpload}
              className="hidden"
            />
          </label>
          
          <label className="flex-1 flex items-center justify-center px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-teal-400 cursor-pointer transition-colors">
            <Upload className="h-5 w-5 text-gray-500 mr-2" />
            <span className="text-gray-600">Upload Image</span>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
          </label>
        </div>

        {isLoading && (
          <div className="text-center py-4">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
            <p className="text-gray-600 mt-2">
              {searchQuery ? 'Processing image...' : 'Searching...'}
            </p>
          </div>
        )}

        {foodInfo && !isLoading && (
          <div className="mt-6 p-4 bg-teal-50 rounded-lg border border-teal-200">
            <h4 className="font-semibold text-teal-900 mb-3">{foodInfo.name}</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div className="text-center">
                <p className="text-2xl font-bold text-teal-700">{foodInfo.calories}</p>
                <p className="text-sm text-teal-600">Calories</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-teal-700">{foodInfo.protein}g</p>
                <p className="text-sm text-teal-600">Protein</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-teal-700">{foodInfo.carbs}g</p>
                <p className="text-sm text-teal-600">Carbs</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-teal-700">{foodInfo.fat}g</p>
                <p className="text-sm text-teal-600">Fat</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-teal-700">{foodInfo.fiber}g</p>
                <p className="text-sm text-teal-600">Fiber</p>
              </div>
            </div>
            {foodInfo.calories === 0 && (
              <p className="text-sm text-teal-600 mt-3 text-center">
                Food not found in database. Try a different search term.
              </p>
            )}
          </div>
        )}

        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <h5 className="font-medium text-gray-900 mb-2">Popular Searches:</h5>
          <div className="flex flex-wrap gap-2">
            {Object.keys(mockFoodDatabase).map((food) => (
              <button
                key={food}
                onClick={() => {
                  setSearchQuery(food);
                  setFoodInfo(mockFoodDatabase[food]);
                }}
                className="px-3 py-1 bg-white border border-gray-300 rounded-full text-sm hover:border-teal-400 transition-colors"
              >
                {food}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FoodSearch;
