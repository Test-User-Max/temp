import { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface User {
  id: string;
  email: string;
  metadata: any;
  preferences: {
    theme: string;
    language: string;
    tts_enabled: boolean;
    voice_speed: number;
  };
}

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    loading: true
  });

  const API_BASE_URL = 'http://localhost:8000';

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('auth_token');
    if (token) {
      validateToken(token);
    } else {
      setAuthState(prev => ({ ...prev, loading: false }));
    }
  }, []);

  const validateToken = async (token: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setAuthState({
        user: response.data.user,
        token,
        loading: false
      });
    } catch (error) {
      localStorage.removeItem('auth_token');
      setAuthState({
        user: null,
        token: null,
        loading: false
      });
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));
      
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password
      });

      const { user, access_token } = response.data;
      
      localStorage.setItem('auth_token', access_token);
      
      setAuthState({
        user,
        token: access_token,
        loading: false
      });

      toast.success('Welcome back!');
    } catch (error: any) {
      setAuthState(prev => ({ ...prev, loading: false }));
      const message = error.response?.data?.detail || 'Login failed';
      toast.error(message);
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));
      
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        email,
        password,
        metadata: { name }
      });

      const { user, access_token } = response.data;
      
      localStorage.setItem('auth_token', access_token);
      
      setAuthState({
        user,
        token: access_token,
        loading: false
      });

      toast.success('Account created successfully!');
    } catch (error: any) {
      setAuthState(prev => ({ ...prev, loading: false }));
      const message = error.response?.data?.detail || 'Registration failed';
      toast.error(message);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setAuthState({
      user: null,
      token: null,
      loading: false
    });
    toast.success('Logged out successfully');
  };

  const updatePreferences = async (preferences: Partial<User['preferences']>) => {
    if (!authState.token) return;

    try {
      const response = await axios.put(
        `${API_BASE_URL}/auth/preferences`,
        preferences,
        {
          headers: { Authorization: `Bearer ${authState.token}` }
        }
      );

      setAuthState(prev => ({
        ...prev,
        user: prev.user ? {
          ...prev.user,
          preferences: { ...prev.user.preferences, ...preferences }
        } : null
      }));

      return response.data;
    } catch (error) {
      console.error('Failed to update preferences:', error);
      throw error;
    }
  };

  return {
    user: authState.user,
    token: authState.token,
    loading: authState.loading,
    isAuthenticated: !!authState.user,
    login,
    register,
    logout,
    updatePreferences
  };
};