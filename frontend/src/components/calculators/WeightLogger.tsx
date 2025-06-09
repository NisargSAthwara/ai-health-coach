
import React, { useState } from 'react';
import { Scale, ArrowLeft, Plus } from 'lucide-react';

interface WeightEntry {
  id: string;
  weight: number;
  date: string;
}

interface WeightLoggerProps {
  onBack: () => void;
}

const WeightLogger: React.FC<WeightLoggerProps> = ({ onBack }) => {
  const [weight, setWeight] = useState('');
  const [entries, setEntries] = useState<WeightEntry[]>([]);

  const addEntry = () => {
    if (weight && parseFloat(weight) > 0) {
      const newEntry: WeightEntry = {
        id: Date.now().toString(),
        weight: parseFloat(weight),
        date: new Date().toISOString().split('T')[0]
      };
      setEntries([newEntry, ...entries]);
      setWeight('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      addEntry();
    }
  };

  const getWeightChange = () => {
    if (entries.length < 2) return null;
    const change = entries[0].weight - entries[1].weight;
    return change;
  };

  const weightChange = getWeightChange();

  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Scale className="h-6 w-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Weight Logger</h3>
        </div>
        <button
          onClick={onBack}
          className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
      </div>

      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
          <input
            type="number"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter weight (kg)"
            step="0.1"
            min="0"
          />
          <button
            onClick={addEntry}
            disabled={!weight || parseFloat(weight) <= 0}
            className="w-full sm:w-auto bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2 min-w-[100px]"
          >
            <Plus className="h-4 w-4" />
            <span>Add</span>
          </button>
        </div>

        {weightChange !== null && (
          <div className={`p-3 rounded-lg ${weightChange < 0 ? 'bg-green-50 border border-green-200' : 'bg-orange-50 border border-orange-200'}`}>
            <p className={`text-sm font-medium ${weightChange < 0 ? 'text-green-700' : 'text-orange-700'}`}>
              {weightChange < 0 ? '↓' : '↑'} {Math.abs(weightChange).toFixed(1)} kg since last entry
            </p>
          </div>
        )}

        <div className="space-y-3 max-h-64 overflow-y-auto">
          <h4 className="font-medium text-gray-900">Weight History</h4>
          {entries.length > 0 ? (
            entries.map((entry, index) => (
              <div key={entry.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg border border-gray-100">
                <div>
                  <p className="font-medium text-gray-900">{entry.weight} kg</p>
                  <p className="text-sm text-gray-600">{new Date(entry.date).toLocaleDateString()}</p>
                </div>
                {index < entries.length - 1 && (
                  <div className="text-right">
                    {entries[index].weight > entries[index + 1].weight ? (
                      <span className="text-orange-600 text-sm font-medium">
                        +{(entries[index].weight - entries[index + 1].weight).toFixed(1)} kg
                      </span>
                    ) : (
                      <span className="text-green-600 text-sm font-medium">
                        -{(entries[index + 1].weight - entries[index].weight).toFixed(1)} kg
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="text-center py-4 text-gray-500">
              <p>No weight entries yet</p>
              <p className="text-sm">Add your first weight entry above</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WeightLogger;
