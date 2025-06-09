
import React, { useState } from 'react';
import { PlusCircle, ArrowLeft, Save } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface AddEntryProps {
  onBack: () => void;
}

interface Entry {
  type: string;
  value: string;
  unit: string;
  notes: string;
}

const AddEntry: React.FC<AddEntryProps> = ({ onBack }) => {
  const [entryType, setEntryType] = useState('');
  const [value, setValue] = useState('');
  const [unit, setUnit] = useState('');
  const [notes, setNotes] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const { isAuthenticated } = useAuth();

  const entryTypes = [
    { id: 'exercise', label: 'Exercise', units: ['minutes', 'hours'] },
    { id: 'food', label: 'Food/Meal', units: ['servings', 'grams', 'cups'] },
    { id: 'water', label: 'Water Intake', units: ['glasses', 'liters', 'ml'] },
    { id: 'sleep', label: 'Sleep', units: ['hours', 'minutes'] },
    { id: 'steps', label: 'Steps', units: ['steps'] },
    { id: 'weight', label: 'Weight', units: ['kg', 'lbs'] }
  ];

  const currentEntryType = entryTypes.find(type => type.id === entryType);

  const handleSubmit = () => {
    if (entryType && value) {
      if (!isAuthenticated) {
        setIsSubmitted(true);
        setTimeout(() => {
          setIsSubmitted(false);
        }, 2000);
        return;
      }

      const entry: Entry = {
        type: entryType,
        value,
        unit,
        notes
      };
      
      // Here you would typically send to backend
      console.log('Saving entry:', entry);
      
      setIsSubmitted(true);
      setTimeout(() => {
        setIsSubmitted(false);
        // Reset form
        setEntryType('');
        setValue('');
        setUnit('');
        setNotes('');
      }, 2000);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <PlusCircle className="h-6 w-6 text-indigo-600" />
          <h3 className="text-lg font-semibold text-gray-900">Add Entry</h3>
        </div>
        <button
          onClick={onBack}
          className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
      </div>

      {isSubmitted ? (
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Save className="h-8 w-8 text-green-600" />
          </div>
          <h4 className="text-lg font-semibold text-green-900 mb-2">{isAuthenticated ? "Entry Saved!" : "Please Log In"}</h4>
      <p className="text-sm text-gray-600">{isAuthenticated ? "Your health data has been recorded successfully." : "Please log in to add the entry."}</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Entry Type
            </label>
            <select
              value={entryType}
              onChange={(e) => {
                setEntryType(e.target.value);
                setUnit(''); // Reset unit when type changes
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select entry type</option>
              {entryTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {entryType && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Value
                  </label>
                  <input
                    type="number"
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="Enter value"
                    step="0.1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Unit
                  </label>
                  <select
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Select unit</option>
                    {currentEntryType?.units.map((unitOption) => (
                      <option key={unitOption} value={unitOption}>
                        {unitOption}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes (optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Add any additional notes..."
                  rows={3}
                />
              </div>

              <button
                onClick={handleSubmit}
                disabled={!entryType || !value || !unit}
                className="w-full bg-indigo-500 text-white py-2 px-4 rounded-md hover:bg-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
              >
                <Save className="h-4 w-4" />
                <span>Save Entry</span>
              </button>
            </>
          )}

          <div className="mt-6 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
            <h4 className="font-semibold text-indigo-900 mb-2">Quick Tips</h4>
            <ul className="text-sm text-indigo-700 space-y-1">
              <li>• Be consistent with your logging for better insights</li>
              <li>• Add notes to track how you feel or circumstances</li>
              <li>• Log entries as close to when they happen as possible</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default AddEntry;
