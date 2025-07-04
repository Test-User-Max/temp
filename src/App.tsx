import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import QueryInput from './components/QueryInput';
import AgentProgress from './components/AgentProgress';
import ResultDisplay from './components/ResultDisplay';
import Footer from './components/Footer';
import { useTheme } from './hooks/useTheme';
import { useApi } from './hooks/useApi';
import './App.css';

interface Step {
  step: number;
  message: string;
  timestamp: number;
  status: string;
}

interface QueryResult {
  query: string;
  intent: string;
  input_type: string;
  research: string;
  summary: string;
  key_points: string[];
  word_count: number;
  confidence: number;
  quality_score: number;
  processing_time: number;
  steps: Step[];
  vision_analysis?: string;
  extracted_text?: string;
  transcription?: string;
  audio?: {
    generated: boolean;
    file?: string;
    duration?: number;
  };
}

function App() {
  const { theme, toggleTheme } = useTheme();
  const { submitQuery, getSessionStatus, loading, checkHealth, apiBaseUrl } = useApi();
  const [result, setResult] = useState<QueryResult | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [steps, setSteps] = useState<Step[]>([]);
  const [showResult, setShowResult] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);
  const [systemHealth, setSystemHealth] = useState<any>(null);

  // Check system health on mount and periodically
  useEffect(() => {
    const checkSystemHealth = async () => {
      const health = await checkHealth();
      setSystemHealth(health);
    };
    
    checkSystemHealth();
    
    // Check health every 30 seconds
    const healthInterval = setInterval(checkSystemHealth, 30000);
    
    return () => clearInterval(healthInterval);
  }, [checkHealth]);

  // Poll backend for agent progress
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (polling && sessionId) {
      interval = setInterval(async () => {
        const status = await getSessionStatus(sessionId);
        if (status && status.steps) {
          setSteps(status.steps);
          setCurrentStep(status.current_step);
          if (status.status === 'completed') {
            setPolling(false);
            setTimeout(() => {
              setResult(status.result);
              setShowResult(true);
            }, 500);
          }
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [polling, sessionId, getSessionStatus]);

  const handleQuerySubmit = async (query: string, enableTts: boolean = false, file?: File) => {
    // Check if backend is available
    if (systemHealth?.status === 'unhealthy') {
      return;
    }

    setResult(null);
    setShowResult(false);
    setCurrentStep(0);
    setSteps([]);
    setSessionId(null);
    setPolling(false);

    try {
      // Generate a session ID for tracking
      const newSessionId = `session_${Date.now()}`;
      setSessionId(newSessionId);
      setPolling(true);
      await submitQuery(query, enableTts, file);
    } catch (error) {
      setPolling(false);
      console.error('Query failed:', error);
    }
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <div className={`min-h-screen transition-all duration-500 relative overflow-hidden ${
      theme === 'dark' 
        ? 'bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900' 
        : 'bg-gradient-to-br from-blue-50 via-white to-blue-100'
    }`}>
      {/* Decorative Background Elements */}
      {theme === 'dark' && (
        <>
          <div className="decorative-circle w-96 h-96 -top-48 -left-48 animate-float" />
          <div className="decorative-circle w-64 h-64 top-1/3 -right-32 animate-float" style={{ animationDelay: '1s' }} />
          <div className="decorative-circle w-80 h-80 bottom-0 left-1/4 animate-float" style={{ animationDelay: '2s' }} />
        </>
      )}

      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: theme === 'dark' ? '#0f172a' : '#ffffff',
            color: theme === 'dark' ? '#f1f5f9' : '#0f172a',
            border: theme === 'dark' ? '1px solid #1e293b' : '1px solid #e2e8f0',
          },
        }}
      />
      
      <Header theme={theme} onToggleTheme={toggleTheme} systemHealth={systemHealth} />
      
      <main className="container mx-auto px-4 py-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto"
        >
          {/* Hero Section */}
          <div className="text-center mb-12">
            <motion.h1 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className={`text-5xl md:text-6xl font-bold mb-6 ${
                theme === 'dark' ? 'text-white' : 'text-slate-900'
              }`}
            >
              <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Neurofluxion
              </span>
              <span className={theme === 'dark' ? 'text-white' : 'text-slate-900'}> AI</span>
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className={`text-xl md:text-2xl mb-4 ${
                theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
              }`}
            >
              Orchestrating Intelligence — Across Voice, Vision, and Thought
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="flex flex-wrap justify-center gap-2 mb-8"
            >
              {['Voice Input', 'Vision Analysis', 'Document Processing', 'LangGraph Orchestration', 'Local AI'].map((feature, index) => (
                <span
                  key={index}
                  className={`px-3 py-1 rounded-full text-sm ${
                    theme === 'dark' 
                      ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border border-cyan-500/30' 
                      : 'bg-gradient-to-r from-cyan-100 to-purple-100 text-cyan-600 border border-cyan-200'
                  }`}
                >
                  {feature}
                </span>
              ))}
            </motion.div>

            {/* Connection Status */}
            {systemHealth?.status === 'unhealthy' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`max-w-md mx-auto p-4 rounded-xl border ${
                  theme === 'dark' 
                    ? 'bg-red-500/10 border-red-500/30 text-red-400' 
                    : 'bg-red-50 border-red-200 text-red-700'
                }`}
              >
                <p className="text-sm font-medium">Backend Connection Required</p>
                <p className="text-xs mt-1 opacity-90">
                  Please start the backend server to use Neurofluxion AI
                </p>
              </motion.div>
            )}
          </div>

          {/* Query Input */}
          <QueryInput 
            onSubmit={handleQuerySubmit} 
            loading={loading}
            theme={theme}
            disabled={systemHealth?.status === 'unhealthy'}
          />

          {/* Agent Progress */}
          <AnimatePresence>
            {loading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="mt-8"
              >
                <AgentProgress 
                  currentStep={currentStep}
                  theme={theme}
                  steps={steps}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Result Display */}
          <AnimatePresence>
            {showResult && result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="mt-8"
              >
                <ResultDisplay 
                  result={result}
                  theme={theme}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </main>

      <Footer theme={theme} />
    </div>
  );
}

export default App;