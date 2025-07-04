import React from 'react';
import { motion } from 'framer-motion';
import { Search, Brain, FileText, Volume2, CheckCircle, Image, Mic, Eye, RotateCcw } from 'lucide-react';

interface AgentProgressProps {
  currentStep: number;
  theme: 'light' | 'dark';
  steps?: Array<{
    step: number;
    message: string;
    timestamp: number;
    status: string;
  }>;
}

const AgentProgress: React.FC<AgentProgressProps> = ({ currentStep, theme, steps = [] }) => {
  const agentSteps = [
    { icon: Search, label: 'Preprocessing', description: 'Analyzing input type and preparing data' },
    { icon: Brain, label: 'Intent Classification', description: 'Understanding query intent and extracting entities' },
    { icon: Eye, label: 'Multimodal Processing', description: 'Processing images, audio, or documents' },
    { icon: Brain, label: 'Research & Analysis', description: 'Gathering information and conducting analysis' },
    { icon: FileText, label: 'Summarization', description: 'Condensing findings into key insights' },
    { icon: RotateCcw, label: 'Quality Control', description: 'Evaluating response quality and improvements' },
    { icon: Volume2, label: 'Audio Generation', description: 'Converting text to speech (if enabled)' },
    { icon: CheckCircle, label: 'Complete', description: 'All agents have finished processing' }
  ];

  // Use steps from props if available, otherwise use default
  const displaySteps = steps.length > 0 ? steps : agentSteps.map((step, index) => ({
    step: index + 1,
    message: step.label,
    timestamp: Date.now(),
    status: index < currentStep ? 'completed' : index === currentStep ? 'active' : 'pending'
  }));

  const progressPercentage = Math.round((currentStep / agentSteps.length) * 100);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className={`rounded-2xl p-6 backdrop-blur-md shadow-xl border relative z-10 ${
        theme === 'dark' 
          ? 'bg-slate-800/40 border-slate-700/50' 
          : 'bg-white/70 border-slate-200/50'
      }`}
    >
      <h3 className={`text-xl font-semibold mb-6 ${
        theme === 'dark' ? 'text-white' : 'text-slate-900'
      }`}>
        LangGraph Agent Pipeline
      </h3>

      {/* Progress Bar */}
      <div className="w-full bg-slate-200/50 rounded-full h-3 mb-6 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progressPercentage}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full relative"
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        </motion.div>
      </div>
      
      <div className="flex justify-between items-center mb-6">
        <span className={`text-sm font-medium ${
          theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
        }`}>
          Progress: {progressPercentage}%
        </span>
        <span className={`text-xs ${
          theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
        }`}>
          Step {Math.min(currentStep, agentSteps.length)} of {agentSteps.length}
        </span>
      </div>

      {/* Agent Steps */}
      <div className="space-y-3">
        {agentSteps.map((step, index) => {
          const Icon = step.icon;
          const stepData = displaySteps.find(s => s.step === index + 1);
          const isActive = currentStep === index + 1;
          const isCompleted = currentStep > index + 1;
          const isPending = currentStep < index + 1;
          
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={`flex items-center p-4 rounded-xl transition-all duration-300 border ${
                isCompleted
                  ? theme === 'dark' 
                    ? 'bg-green-500/20 border-green-500/50' 
                    : 'bg-green-50/80 border-green-200/50'
                  : isActive
                    ? theme === 'dark' 
                      ? 'bg-blue-500/20 border-blue-500/50' 
                      : 'bg-blue-50/80 border-blue-200/50'
                    : theme === 'dark' 
                      ? 'bg-slate-700/30 border-slate-600/30' 
                      : 'bg-slate-50/50 border-slate-200/30'
              }`}
            >
              <div className={`p-3 rounded-lg mr-4 transition-all duration-300 ${
                isCompleted
                  ? 'bg-green-500 text-white' 
                  : isActive
                    ? 'bg-blue-500 text-white'
                    : theme === 'dark' 
                      ? 'bg-slate-600 text-slate-300' 
                      : 'bg-slate-200 text-slate-600'
              }`}>
                <Icon size={20} />
              </div>
              
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className={`font-medium ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    {stepData?.message || step.label}
                  </h4>
                  
                  {isActive && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"
                    />
                  )}
                  
                  {isCompleted && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      <CheckCircle size={16} className="text-green-500" />
                    </motion.div>
                  )}
                </div>
                
                <p className={`text-sm mt-1 ${
                  theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
                }`}>
                  {step.description}
                </p>
                
                {stepData?.timestamp && isActive && (
                  <p className={`text-xs mt-1 ${
                    theme === 'dark' ? 'text-slate-500' : 'text-slate-400'
                  }`}>
                    Started: {new Date(stepData.timestamp * 1000).toLocaleTimeString()}
                  </p>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Agent Architecture Info */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        className={`mt-6 p-4 rounded-lg ${
          theme === 'dark' ? 'bg-slate-700/30' : 'bg-slate-50/50'
        }`}
      >
        <h5 className={`text-sm font-medium mb-2 ${
          theme === 'dark' ? 'text-white' : 'text-slate-900'
        }`}>
          LangGraph Orchestration
        </h5>
        <p className={`text-xs ${
          theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
        }`}>
          Intelligent agent routing with conditional edges, quality control loops, and multi-modal processing capabilities.
        </p>
      </motion.div>
    </motion.div>
  );
};

export default AgentProgress;