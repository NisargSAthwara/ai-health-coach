
import React, { useState, useEffect } from 'react';
import { Send, Bot, User, Loader2, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { useAuth } from '../context/AuthContext';

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
      text: "Hello! I'm your AI Health & Nutrition Assistant. I can help you track your fitness goals, provide nutrition advice, calculate your BMI, and much more. Please log in to unlock full features.",
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
  const [currentWeight, setCurrentWeight] = useState('');
  const [height, setHeight] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [hasGoal, setHasGoal] = useState(false);
  const [goalModalMessage, setGoalModalMessage] = useState('');
  const { token, isAuthenticated, logout } = useAuth();

  useEffect(() => {
    // Clear messages on page load if not authenticated
    if (!localStorage.getItem("access_token")) {
      setMessages([]);
    }

    const fetchGoalStatus = async () => {
      if (isAuthenticated && token) {
        try {
          const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/goal/get`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          if (response.ok) {
            const data = await response.json();
            setHasGoal(true);
            setMessages(prev => [...prev, {
              id: Date.now().toString(),
              text: `Welcome back! Your current goal is: ${data.goal_text}. How can I help you today?`,
              isUser: false,
              timestamp: new Date()
            }]);
          } else if (response.status === 404) {
            setHasGoal(false);
            setMessages(prev => [...prev, {
              id: Date.now().toString(),
              text: "Welcome! It looks like you haven't set a health goal yet. Would you like to set one to get personalized advice?",
              isUser: false,
              timestamp: new Date()
            }]);
          } else {
            console.error("Failed to fetch goal status");
            setHasGoal(false);
          }
        } catch (error) {
          console.error("Error fetching goal status:", error);
          setHasGoal(false);
        }
      }
    };

    fetchGoalStatus();
  }, [isAuthenticated, token]);

  useEffect(() => {
    if (!isAuthenticated) {
      setMessages([]);
    }
  }, [isAuthenticated]);

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

    // Allow unauthenticated users to use the chatbot for basic Q&A
    if (!isAuthenticated || !token) {
      const predefinedResponses: { [key: string]: string } = {
        "hello": "Hello there! How can I help you today?",
        "hi": "Hi! What's on your mind?",
        "how are you": "I'm an AI, so I don't have feelings, but I'm ready to assist you!",
        "what can you do": "I can help you track your fitness goals, provide nutrition advice, calculate your BMI, and much more. What would you like to know?",
        "who are you": "I am your AI Health & Nutrition Assistant, here to help you on your wellness journey.",
        "thank you": "You're welcome! Let me know if you need anything else.",
        "bye": "Goodbye! Have a healthy day!",
        "default": "I'm sorry, I can only answer basic questions for now. Please log in to unlock full features."
      };

      const lowerCaseInput = inputText.toLowerCase();
      const responseText = predefinedResponses[lowerCaseInput] || predefinedResponses["default"];

      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
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
    if (!goalType || !targetWeight || !timeframe || !activityLevel || !currentWeight || !height || !age || !gender) {
      setGoalModalMessage("Please fill in all required goal fields.");
      return;
    }

    if (isNaN(Number(targetWeight)) || isNaN(Number(currentWeight)) || isNaN(Number(height)) || isNaN(Number(age))) {
      setGoalModalMessage("Target Weight, Current Weight, Height, and Age must be numbers.");
      return;
    }

    const goalData = {
      goal_type: goalType,
      target_weight: parseFloat(targetWeight),
      timeframe: timeframe,
      activity_level: activityLevel,
      dietary_preferences: dietaryPreferences,
      allergies: allergies,
      current_weight: parseFloat(currentWeight),
      height: parseFloat(height),
      age: parseInt(age),
      gender: gender,
    };

    if (!isAuthenticated || !token) {
      setGoalModalMessage("Please log in to set a goal.");
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/goal/set`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(goalData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
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
    } catch (error: any) {
      console.error("Error setting goal:", error);
      setGoalModalMessage(error.message || "Failed to set goal. Please try again.");

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
      <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-emerald-500 to-teal-500 flex-shrink-0 rounded-t-lg">
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
          <Dialog open={showGoalModal} onOpenChange={(open) => {
            setShowGoalModal(open);
            setGoalModalMessage(''); // Clear message when modal opens or closes
          }}>
            <DialogTrigger asChild>
              <Button variant="outline" className="ml-auto">
                <Settings className="mr-2 h-4 w-4" /> Set Goal
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px] md:max-w-[600px] lg:max-w-[700px] overflow-y-auto max-h-[90vh]">
              <DialogHeader>
                <DialogTitle>Set Your Health Goal</DialogTitle>
                <DialogDescription className="text-mauve11 mt-[10px] mb-5 text-[15px] leading-normal">
                  Set your health goals to get personalized recommendations.
                </DialogDescription>
              </DialogHeader>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-4">
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="goalType" className="text-right">Goal Type</Label>
                  <Select onValueChange={setGoalType} value={goalType} required>
                    <SelectTrigger className="col-span-3"><SelectValue placeholder="Select a goal" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="weight_loss">Weight Loss</SelectItem>
                      <SelectItem value="muscle_gain">Muscle Gain</SelectItem>
                      <SelectItem value="healthy_eating">Healthy Eating</SelectItem>
                      <SelectItem value="overall_fitness">Overall Fitness</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="currentWeight" className="text-right">Current Weight (kg)</Label>
                  <Input id="currentWeight" type="number" value={currentWeight} onChange={(e) => setCurrentWeight(e.target.value)} className="col-span-3" required />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="targetWeight" className="text-right">Target Weight (kg)</Label>
                  <Input id="targetWeight" type="number" value={targetWeight} onChange={(e) => setTargetWeight(e.target.value)} className="col-span-3" required />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="height" className="text-right">Height (cm)</Label>
                  <Input id="height" type="number" value={height} onChange={(e) => setHeight(e.target.value)} className="col-span-3" required />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="age" className="text-right">Age</Label>
                  <Input id="age" type="number" value={age} onChange={(e) => setAge(e.target.value)} className="col-span-3" required />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="gender" className="text-right">Gender</Label>
                  <Select onValueChange={setGender} value={gender} required>
                    <SelectTrigger className="col-span-3"><SelectValue placeholder="Select gender" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="timeframe" className="text-right">Timeframe</Label>
                  <Input id="timeframe" value={timeframe} onChange={(e) => setTimeframe(e.target.value)} className="col-span-3" placeholder="e.g., 3 months, 6 weeks" required />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="activityLevel" className="text-right">Activity Level</Label>
                  <Select onValueChange={setActivityLevel} value={activityLevel} required>
                    <SelectTrigger className="col-span-3"><SelectValue placeholder="Select activity level" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sedentary">Sedentary</SelectItem>
                      <SelectItem value="lightly_active">Lightly Active</SelectItem>
                      <SelectItem value="moderately_active">Moderately Active</SelectItem>
                      <SelectItem value="very_active">Very Active</SelectItem>
                      <SelectItem value="extra_active">Extra Active</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="dietaryPreferences" className="text-right">Dietary Preferences (Optional)</Label>
                  <Textarea id="dietaryPreferences" value={dietaryPreferences} onChange={(e) => setDietaryPreferences(e.target.value)} className="col-span-3" placeholder="e.g., Vegetarian, Vegan, Keto" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 items-center gap-4">
                  <Label htmlFor="allergies" className="text-right">Allergies (Optional)</Label>
                  <Textarea id="allergies" value={allergies} onChange={(e) => setAllergies(e.target.value)} className="col-span-3" placeholder="e.g., Peanuts, Gluten, Dairy" />
                </div>
                {goalModalMessage && (
                  <div className="col-span-full text-center text-red-500 text-sm mt-2 mb-4">
                    {goalModalMessage}
                  </div>
                )}
              </div>
              <DialogFooter>
                <Button type="submit" onClick={handleSubmitGoal}>Set Goal</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
        {hasGoal && (
          <div className="text-center text-sm text-gray-600 mb-4 p-2 bg-blue-50 rounded-md">
            Using your goals for personalized advice.
          </div>
        )}
        {messages.map((message) => (
          <div key={message.id} className={`flex mb-4 ${message.isUser ? 'justify-end' : 'justify-start'} items-end`}>
            {!message.isUser && (
              <div className="bg-gray-200 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0 mb-4 mr-2">
                <Bot className="h-4 w-4 text-gray-600" />
              </div>
            )}
            {!message.isUser && (
              <div className="flex flex-col space-y-2 text-base max-w-xs items-start">
                <div className="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-200 text-gray-800 shadow-md">
                  {message.text}
                </div>
                <span className="text-xs text-gray-500">{message.timestamp.toLocaleTimeString([], { hour: 'numeric', minute: 'numeric' })}</span>
              </div>
            )}
            {message.isUser && (
              <div className="flex flex-col space-y-2 text-base max-w-xs items-end">
                <div className="px-4 py-2 rounded-lg inline-block rounded-br-none bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-md">
                  {message.text}
                </div>
                <span className="text-xs text-gray-500">{message.timestamp.toLocaleTimeString([], { hour: 'numeric', minute: 'numeric' })}</span>
              </div>
            )}
            {message.isUser && (
              <div className="bg-gradient-to-r from-emerald-500 to-teal-500 p-2 rounded-full flex-shrink-0 mb-4 ml-2">
                <User className="h-5 w-5 text-white" />
              </div>
            )}
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
