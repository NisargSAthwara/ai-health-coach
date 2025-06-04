
import React, { useState, useEffect } from 'react';
import { Send, Bot, User, Loader2, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your AI Health & Nutrition Assistant. I can help you track your fitness goals, provide nutrition advice, calculate your BMI, and much more. What would you like to know?",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [goalType, setGoalType] = useState('');
  const [targetWeight, setTargetWeight] = useState('');
  const [timeframe, setTimeframe] = useState('');
  const [activityLevel, setActivityLevel] = useState('');
  const [dietaryPreferences, setDietaryPreferences] = useState('');
  const [allergies, setAllergies] = useState('');
  const [hasGoal, setHasGoal] = useState(false);

  useEffect(() => {
    // Check if a goal is already set (e.g., from local storage or a backend call)
    const goalStatus = localStorage.getItem('hasGoal');
    if (goalStatus === 'true') {
      setHasGoal(true);
    }
  }, []);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputText }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response, // Assuming the backend sends a 'response' field
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I'm having trouble connecting right now. Please try again later.",
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitGoal = async () => {
    // Prepare goal data
    const goalDescription = `Goal Type: ${goalType}, Target Weight: ${targetWeight}kg, Timeframe: ${timeframe}, Activity Level: ${activityLevel}, Dietary Preferences: ${dietaryPreferences}, Allergies: ${allergies}`;

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/goal/set`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ goal_description: goalDescription }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Goal set successfully:', result);
      setHasGoal(true);
      localStorage.setItem('hasGoal', 'true'); // Store goal status
      setShowGoalModal(false); // Close modal on success
      // Optionally, refresh chat context or display a message
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: "Goal set! Now receiving personalized advice.",
        isUser: false,
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error("Error setting goal:", error);
      alert("Failed to set goal. Please try again.");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col bg-white rounded-lg shadow-sm border border-gray-200 h-[700px] lg:h-[850px]">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-teal-50 flex-shrink-0 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-emerald-500 to-teal-500 p-2 rounded-full flex-shrink-0">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">AI Health Assistant</h3>
              <p className="text-sm text-gray-600">Always here to help with your wellness journey</p>
            </div>
          </div>
          <Dialog open={showGoalModal} onOpenChange={setShowGoalModal}>
            <DialogTrigger asChild>
              <Button variant="outline" className="ml-auto">
                <Settings className="mr-2 h-4 w-4" /> Set Goal
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Set Your Goal</DialogTitle>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="goalType" className="text-right">Goal Type</Label>
                  <Select onValueChange={setGoalType} value={goalType}>
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Select a goal type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="weight_loss">Weight Loss</SelectItem>
                      <SelectItem value="muscle_gain">Muscle Gain</SelectItem>
                      <SelectItem value="healthy_eating">Healthy Eating</SelectItem>
                      <SelectItem value="general_wellness">General Wellness</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="targetWeight" className="text-right">Target Weight (kg)</Label>
                  <Input id="targetWeight" type="number" value={targetWeight} onChange={(e) => setTargetWeight(e.target.value)} className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="timeframe" className="text-right">Timeframe</Label>
                  <Input id="timeframe" value={timeframe} onChange={(e) => setTimeframe(e.target.value)} className="col-span-3" placeholder="e.g., 3 months, 6 weeks" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="activityLevel" className="text-right">Activity Level</Label>
                  <Select onValueChange={setActivityLevel} value={activityLevel}>
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Select activity level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sedentary">Sedentary</SelectItem>
                      <SelectItem value="lightly_active">Lightly Active</SelectItem>
                      <SelectItem value="moderately_active">Moderately Active</SelectItem>
                      <SelectItem value="very_active">Very Active</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="dietaryPreferences" className="text-right">Dietary Preferences</Label>
                  <Textarea id="dietaryPreferences" value={dietaryPreferences} onChange={(e) => setDietaryPreferences(e.target.value)} className="col-span-3" placeholder="e.g., Vegetarian, Vegan, Keto" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="allergies" className="text-right">Allergies</Label>
                  <Textarea id="allergies" value={allergies} onChange={(e) => setAllergies(e.target.value)} className="col-span-3" placeholder="e.g., Peanuts, Gluten, Dairy" />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowGoalModal(false)}>Cancel</Button>
                <Button type="submit" onClick={handleSubmitGoal}>Save Goal</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {hasGoal && (
          <div className="text-center text-sm text-gray-600 mb-4 p-2 bg-blue-50 rounded-md">
            Using your goals for personalized advice.
          </div>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}
          >
            <div className={`flex max-w-xs lg:max-w-md items-start space-x-3 ${message.isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${message.isUser ? 'bg-emerald-500' : 'bg-gray-200'}`}>
                {message.isUser ? (
                  <User className="h-4 w-4 text-white" />
                ) : (
                  <Bot className="h-4 w-4 text-gray-600" />
                )}
              </div>
              <div
                className={`px-4 py-2 rounded-2xl max-w-full ${
                  message.isUser
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="text-sm leading-relaxed break-words">{message.text}</p>
                <p className={`text-xs mt-1 ${message.isUser ? 'text-emerald-100' : 'text-gray-500'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="flex max-w-xs lg:max-w-md items-start space-x-3">
              <div className="bg-gray-200 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                <Bot className="h-4 w-4 text-gray-600" />
              </div>
              <div className="bg-gray-100 px-4 py-2 rounded-2xl">
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
                  <p className="text-sm text-gray-600">Thinking...</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-100 flex-shrink-0">
        <div className="flex space-x-3">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about nutrition, fitness, or health goals..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isLoading}
            className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white p-2 rounded-lg hover:from-emerald-600 hover:to-teal-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">Press Enter to send</p>
      </div>
    </div>
  );
};

export default ChatInterface;
