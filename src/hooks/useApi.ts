import { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

// Dynamic API base URL detection
const getApiBaseUrl = () => {
  // Check if we're in development mode
  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }
  
  // For production or WebContainer environments
  const currentUrl = window.location;
  const port = '8000';
  
  // Try to construct the backend URL based on current frontend URL
  if (currentUrl.hostname.includes('webcontainer-api.io')) {
    // WebContainer environment - use the same hostname with port 8000
    const backendHostname = currentUrl.hostname.replace('5173', '8000');
    return `${currentUrl.protocol}//${backendHostname}`;
  }
  
  // Default fallback
  return `${currentUrl.protocol}//${currentUrl.hostname}:${port}`;
};

const API_BASE_URL = getApiBaseUrl();

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitQuery = async (
    query: string, 
    enableTts: boolean = false, 
    file?: File, 
    language: string = 'en',
    enableStreaming: boolean = false
  ) => {
    setLoading(true);
    setError(null);

    try {
      let response;
      
      if (file) {
        // Handle file upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('query', query);
        formData.append('enable_tts', enableTts.toString());
        formData.append('language', language);
        formData.append('session_id', `session_${Date.now()}`);

        response = await axios.post(`${API_BASE_URL}/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000, // 60 second timeout
        });
      } else {
        // Handle text query
        response = await axios.post(`${API_BASE_URL}/ask`, {
          query,
          enable_tts: enableTts,
          language,
          enable_streaming: enableStreaming,
          session_id: `session_${Date.now()}`
        }, {
          timeout: 60000, // 60 second timeout
        });
      }

      if (response.data.status === 'success') {
        toast.success('Query processed successfully!');
        return response.data;
      } else {
        throw new Error(response.data.message || 'Unknown error');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to process query';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`, {
        timeout: 10000, // 10 second timeout for health check
      });
      return response.data;
    } catch (err: any) {
      console.error('Health check failed:', err);
      
      // Provide more specific error information
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        console.warn(`Backend not accessible at ${API_BASE_URL}. Please ensure the backend server is running.`);
        return {
          status: 'unhealthy',
          error: 'Backend server not accessible',
          backend_url: API_BASE_URL,
          suggestion: 'Start the backend server with: cd backend && python main.py'
        };
      }
      
      return {
        status: 'unhealthy',
        error: err.message,
        backend_url: API_BASE_URL
      };
    }
  };

  const getSessionStatus = async (sessionId: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/status/${sessionId}`, {
        timeout: 10000,
      });
      return response.data;
    } catch (err) {
      console.error('Status check failed:', err);
      return null;
    }
  };

  const getSessionHistory = async (sessionId: string, limit: number = 10) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/conversations/${sessionId}/history?limit=${limit}`, {
        timeout: 10000,
      });
      return response.data;
    } catch (err) {
      console.error('History fetch failed:', err);
      return null;
    }
  };

  const searchDocuments = async (query: string, limit: number = 5) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/search?query=${encodeURIComponent(query)}&limit=${limit}`, {
        timeout: 15000,
      });
      return response.data;
    } catch (err) {
      console.error('Document search failed:', err);
      return null;
    }
  };

  const addDocument = async (filePath: string, chunkSize: number = 1000, overlap: number = 200) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/documents/add`, {
        file_path: filePath,
        chunk_size: chunkSize,
        overlap: overlap
      }, {
        timeout: 30000,
      });
      return response.data;
    } catch (err) {
      console.error('Document addition failed:', err);
      throw err;
    }
  };

  const getSystemStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`, {
        timeout: 10000,
      });
      return response.data;
    } catch (err) {
      console.error('Stats fetch failed:', err);
      return null;
    }
  };

  const getAgents = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents`, {
        timeout: 10000,
      });
      return response.data;
    } catch (err) {
      console.error('Agents fetch failed:', err);
      return null;
    }
  };

  const getSupportedLanguages = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/languages`, {
        timeout: 10000,
      });
      return response.data;
    } catch (err) {
      console.error('Languages fetch failed:', err);
      return null;
    }
  };

  const translateText = async (text: string, targetLanguage: string, sourceLanguage?: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/translate`, null, {
        params: {
          text,
          target_language: targetLanguage,
          source_language: sourceLanguage
        },
        timeout: 15000,
      });
      return response.data;
    } catch (err) {
      console.error('Translation failed:', err);
      return null;
    }
  };

  return {
    submitQuery,
    checkHealth,
    getSessionStatus,
    getSessionHistory,
    searchDocuments,
    addDocument,
    getSystemStats,
    getAgents,
    getSupportedLanguages,
    translateText,
    loading,
    error,
    apiBaseUrl: API_BASE_URL
  };
};