import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Code, 
  Eye, 
  EyeOff, 
  Download, 
  Trash2, 
  Clock, 
  Zap, 
  AlertCircle,
  CheckCircle,
  Info,
  Filter
} from 'lucide-react';

interface DeveloperPanelProps {
  theme: 'light' | 'dark';
  sessionId: string | null;
  isVisible: boolean;
  onToggle: () => void;
}

interface LogEntry {
  timestamp: string;
  session_id: string;
  type: string;
  agent_name?: string;
  execution_time?: number;
  prompt_used?: string;
  model_response?: string;
  error_message?: string;
  data?: any;
}

const DeveloperPanel: React.FC<DeveloperPanelProps> = ({ 
  theme, 
  sessionId, 
  isVisible, 
  onToggle 
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
  const [selectedLogType, setSelectedLogType] = useState<string>('all');
  const [selectedAgent, setSelectedAgent] = useState<string>('all');
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Mock data for demonstration
  useEffect(() => {
    if (sessionId && isVisible) {
      // Simulate fetching logs
      const mockLogs: LogEntry[] = [
        {
          timestamp: new Date().toISOString(),
          session_id: sessionId,
          type: 'agent_execution',
          agent_name: 'IntentAgent',
          execution_time: 0.234,
          prompt_used: 'Analyze the following query and classify its intent...',
          model_response: 'Intent: research, Confidence: 0.9'
        },
        {
          timestamp: new Date().toISOString(),
          session_id: sessionId,
          type: 'llm_call',
          agent_name: 'ResearchAgent',
          execution_time: 2.456,
          prompt_used: 'Provide comprehensive research on: artificial intelligence',
          model_response: 'Artificial intelligence (AI) is a branch of computer science...'
        },
        {
          timestamp: new Date().toISOString(),
          session_id: sessionId,
          type: 'vector_search',
          data: { query: 'AI research', results_count: 5, similarity_scores: [0.89, 0.76, 0.65] }
        },
        {
          timestamp: new Date().toISOString(),
          session_id: sessionId,
          type: 'user_interaction',
          data: { interaction_type: 'query_submit', query: 'Tell me about AI' }
        }
      ];
      
      setLogs(mockLogs);
      
      // Mock performance metrics
      setPerformanceMetrics({
        total_execution_time: 3.2,
        agent_count: 4,
        agent_average_times: {
          'IntentAgent': 0.234,
          'ResearchAgent': 2.456,
          'SummarizerAgent': 0.456,
          'TTSAgent': 1.234
        },
        slowest_agent: ['ResearchAgent', 2.456],
        fastest_agent: ['IntentAgent', 0.234]
      });
    }
  }, [sessionId, isVisible]);

  // Filter logs
  useEffect(() => {
    let filtered = logs;
    
    if (selectedLogType !== 'all') {
      filtered = filtered.filter(log => log.type === selectedLogType);
    }
    
    if (selectedAgent !== 'all') {
      filtered = filtered.filter(log => log.agent_name === selectedAgent);
    }
    
    setFilteredLogs(filtered);
  }, [logs, selectedLogType, selectedAgent]);

  const logTypes = ['all', 'agent_execution', 'llm_call', 'vector_search', 'user_interaction', 'error'];
  const agents = ['all', 'IntentAgent', 'ResearchAgent', 'SummarizerAgent', 'TTSAgent', 'VisionAgent'];

  const getLogIcon = (type: string) => {
    switch (type) {
      case 'agent_execution': return <Zap size={16} className="text-blue-500" />;
      case 'llm_call': return <Code size={16} className="text-purple-500" />;
      case 'vector_search': return <Info size={16} className="text-green-500" />;
      case 'user_interaction': return <CheckCircle size={16} className="text-cyan-500" />;
      case 'error': return <AlertCircle size={16} className="text-red-500" />;
      default: return <Info size={16} className="text-gray-500" />;
    }
  };

  const exportLogs = () => {
    const dataStr = JSON.stringify(filteredLogs, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `debug_logs_${sessionId}_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const clearLogs = () => {
    setLogs([]);
    setFilteredLogs([]);
  };

  if (!isVisible) {
    return (
      <motion.button
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={onToggle}
        className={`fixed bottom-4 right-4 p-3 rounded-full shadow-lg z-50 ${
          theme === 'dark'
            ? 'bg-slate-800 hover:bg-slate-700 text-white border border-slate-700'
            : 'bg-white hover:bg-gray-50 text-slate-900 border border-gray-200'
        }`}
      >
        <Code size={20} />
      </motion.button>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: '100%' }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: '100%' }}
      className={`fixed top-0 right-0 h-full w-96 shadow-2xl z-50 overflow-hidden ${
        theme === 'dark'
          ? 'bg-slate-900 border-l border-slate-700'
          : 'bg-white border-l border-gray-200'
      }`}
    >
      {/* Header */}
      <div className={`p-4 border-b ${
        theme === 'dark' ? 'border-slate-700' : 'border-gray-200'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Code size={20} className="text-blue-500" />
            <h3 className={`font-semibold ${
              theme === 'dark' ? 'text-white' : 'text-slate-900'
            }`}>
              Developer Panel
            </h3>
          </div>
          
          <div className="flex items-center space-x-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={exportLogs}
              className={`p-1 rounded ${
                theme === 'dark' 
                  ? 'hover:bg-slate-700 text-slate-400' 
                  : 'hover:bg-gray-100 text-slate-600'
              }`}
            >
              <Download size={16} />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={clearLogs}
              className={`p-1 rounded ${
                theme === 'dark' 
                  ? 'hover:bg-slate-700 text-slate-400' 
                  : 'hover:bg-gray-100 text-slate-600'
              }`}
            >
              <Trash2 size={16} />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onToggle}
              className={`p-1 rounded ${
                theme === 'dark' 
                  ? 'hover:bg-slate-700 text-slate-400' 
                  : 'hover:bg-gray-100 text-slate-600'
              }`}
            >
              <EyeOff size={16} />
            </motion.button>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      {performanceMetrics && (
        <div className={`p-4 border-b ${
          theme === 'dark' ? 'border-slate-700' : 'border-gray-200'
        }`}>
          <h4 className={`text-sm font-medium mb-2 ${
            theme === 'dark' ? 'text-white' : 'text-slate-900'
          }`}>
            Performance Metrics
          </h4>
          
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className={`p-2 rounded ${
              theme === 'dark' ? 'bg-slate-800' : 'bg-gray-50'
            }`}>
              <div className={theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}>
                Total Time
              </div>
              <div className={`font-mono ${
                theme === 'dark' ? 'text-white' : 'text-slate-900'
              }`}>
                {performanceMetrics.total_execution_time}s
              </div>
            </div>
            
            <div className={`p-2 rounded ${
              theme === 'dark' ? 'bg-slate-800' : 'bg-gray-50'
            }`}>
              <div className={theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}>
                Agents
              </div>
              <div className={`font-mono ${
                theme === 'dark' ? 'text-white' : 'text-slate-900'
              }`}>
                {performanceMetrics.agent_count}
              </div>
            </div>
          </div>
          
          {performanceMetrics.slowest_agent && (
            <div className="mt-2 text-xs">
              <span className={theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}>
                Slowest: 
              </span>
              <span className={`ml-1 font-mono ${
                theme === 'dark' ? 'text-red-400' : 'text-red-600'
              }`}>
                {performanceMetrics.slowest_agent[0]} ({performanceMetrics.slowest_agent[1]}s)
              </span>
            </div>
          )}
        </div>
      )}

      {/* Filters */}
      <div className={`p-4 border-b ${
        theme === 'dark' ? 'border-slate-700' : 'border-gray-200'
      }`}>
        <div className="flex items-center space-x-2 mb-2">
          <Filter size={16} className="text-blue-500" />
          <span className={`text-sm font-medium ${
            theme === 'dark' ? 'text-white' : 'text-slate-900'
          }`}>
            Filters
          </span>
        </div>
        
        <div className="space-y-2">
          <select
            value={selectedLogType}
            onChange={(e) => setSelectedLogType(e.target.value)}
            className={`w-full text-xs p-2 rounded border ${
              theme === 'dark'
                ? 'bg-slate-800 border-slate-600 text-white'
                : 'bg-white border-gray-300 text-slate-900'
            }`}
          >
            {logTypes.map(type => (
              <option key={type} value={type}>
                {type === 'all' ? 'All Types' : type.replace('_', ' ')}
              </option>
            ))}
          </select>
          
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className={`w-full text-xs p-2 rounded border ${
              theme === 'dark'
                ? 'bg-slate-800 border-slate-600 text-white'
                : 'bg-white border-gray-300 text-slate-900'
            }`}
          >
            {agents.map(agent => (
              <option key={agent} value={agent}>
                {agent === 'all' ? 'All Agents' : agent}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Logs */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          {filteredLogs.map((log, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`p-3 rounded-lg border text-xs ${
                theme === 'dark'
                  ? 'bg-slate-800 border-slate-700'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {getLogIcon(log.type)}
                  <span className={`font-medium ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    {log.agent_name || log.type}
                  </span>
                </div>
                
                {log.execution_time && (
                  <div className="flex items-center space-x-1">
                    <Clock size={12} className="text-gray-500" />
                    <span className={theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}>
                      {log.execution_time}s
                    </span>
                  </div>
                )}
              </div>
              
              <div className={`text-xs ${
                theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
              }`}>
                {new Date(log.timestamp).toLocaleTimeString()}
              </div>
              
              {log.prompt_used && (
                <div className="mt-2">
                  <div className={`text-xs font-medium ${
                    theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                  }`}>
                    Prompt:
                  </div>
                  <div className={`text-xs mt-1 p-2 rounded font-mono ${
                    theme === 'dark' ? 'bg-slate-900 text-slate-400' : 'bg-white text-slate-600'
                  }`}>
                    {log.prompt_used.substring(0, 100)}...
                  </div>
                </div>
              )}
              
              {log.model_response && (
                <div className="mt-2">
                  <div className={`text-xs font-medium ${
                    theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                  }`}>
                    Response:
                  </div>
                  <div className={`text-xs mt-1 p-2 rounded font-mono ${
                    theme === 'dark' ? 'bg-slate-900 text-slate-400' : 'bg-white text-slate-600'
                  }`}>
                    {log.model_response.substring(0, 100)}...
                  </div>
                </div>
              )}
              
              {log.data && (
                <div className="mt-2">
                  <div className={`text-xs font-medium ${
                    theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                  }`}>
                    Data:
                  </div>
                  <div className={`text-xs mt-1 p-2 rounded font-mono ${
                    theme === 'dark' ? 'bg-slate-900 text-slate-400' : 'bg-white text-slate-600'
                  }`}>
                    {JSON.stringify(log.data, null, 2).substring(0, 200)}...
                  </div>
                </div>
              )}
            </motion.div>
          ))}
          
          {filteredLogs.length === 0 && (
            <div className={`text-center py-8 ${
              theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
            }`}>
              No logs available
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default DeveloperPanel;