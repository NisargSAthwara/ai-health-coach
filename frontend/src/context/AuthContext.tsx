import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
  // Add other user-related fields as needed
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (newToken: string, userData: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    const expiry = localStorage.getItem('expires_at');

    if (storedToken && expiry) {
      if (Date.now() > Number(expiry)) {
        console.warn("Token expired. Logging out.");
        logout(); // Use the logout function to clear all related state
      } else {
        setToken(storedToken);
        // In a real application, you would decode the token or fetch user data
        // from an API here to re-hydrate the user state on refresh.
        // For now, we'll assume user data is passed during login.
      }
    } else if (!storedToken && expiry) {
      // If for some reason token is gone but expiry remains, clear it
      localStorage.removeItem('expires_at');
    }
  }, []);

  const login = (newToken: string, userData: User) => {
    setToken(newToken);
    setUser(userData);
    localStorage.setItem('access_token', newToken);
    localStorage.setItem('expires_at', (Date.now() + 3600000).toString()); // 1 hour expiry
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('expires_at');
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};