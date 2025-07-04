import React from 'react';
import { motion } from 'framer-motion';
import { Moon, Sun, Zap, AlertCircle, CheckCircle, Server } from 'lucide-react';

interface HeaderProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  systemHealth?: any;
}

const Header: React.FC<HeaderProps> = ({ theme, onToggleTheme, systemHealth }) => {
  const getHealthStatus = () => {
    if (!systemHealth) return { icon: AlertCircle, text: 'Checking...', color: 'text-gray-500' };
    
    if (systemHealth.status === 'healthy' && systemHealth.ollama_status === 'connected') {
      return { icon: CheckCircle, text: 'All Systems Online', color: 'text-green-500' };
    } else if (systemHealth.status === 'unhealthy') {
      return { icon: AlertCircle, text: 'Backend Offline', color: 'text-red-500' };
    } else if (systemHealth.ollama_status === 'disconnected') {
      return { icon: AlertCircle, text: 'Ollama Disconnected', color: 'text-red-500' };
    } else {
      return { icon: AlertCircle, text: 'Partial Service', color: 'text-yellow-500' };
    }
  };

  const healthStatus = getHealthStatus();
  const HealthIcon = healthStatus.icon;

  return (
    <motion.header 
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`backdrop-blur-md border-b transition-all duration-300 relative z-20 ${
        theme === 'dark' 
          ? 'bg-slate-900/30 border-slate-800/50' 
          : 'bg-white/50 border-slate-200/50'
      }`}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="flex items-center space-x-3"
          >
            <div className={`p-2 rounded-xl ${
              theme === 'dark' 
                ? 'bg-gradient-to-br from-cyan-500/20 to-purple-500/20 text-cyan-400' 
                : 'bg-gradient-to-br from-cyan-500/10 to-purple-500/10 text-cyan-600'
            }`}>
              <img 
                src="/logo.jpg" 
                alt="Neurofluxion AI" 
                className="w-6 h-6 rounded-lg"
                onError={(e) => {
                  // Fallback to icon if logo fails to load
                  e.currentTarget.style.display = 'none';
                  e.currentTarget.nextElementSibling!.style.display = 'block';
                }}
              />
              <Zap size={24} style={{ display: 'none' }} />
            </div>
            <div>
              <h1 className={`text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent`}>
                Neurofluxion AI
              </h1>
              <p className={`text-sm ${
                theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
              }`}>
                Orchestrating Intelligence
              </p>
            </div>
          </motion.div>

          {/* Status & Theme Toggle */}
          <div className="flex items-center space-x-4">
            {/* System Health Status */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex items-center space-x-2"
            >
              <div className="flex items-center space-x-1">
                <HealthIcon size={16} className={healthStatus.color} />
                <span className={`text-sm ${
                  theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
                }`}>
                  {healthStatus.text}
                </span>
              </div>
              
              {/* Backend Status Indicator */}
              {systemHealth?.status === 'unhealthy' && (
                <div className={`text-xs px-2 py-1 rounded ${
                  theme === 'dark' 
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                    : 'bg-red-100 text-red-600 border border-red-200'
                }`}>
                  <div className="flex items-center space-x-1">
                    <Server size={12} />
                    <span>Backend Required</span>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Model Info */}
            {systemHealth?.config && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className={`text-xs px-2 py-1 rounded ${
                  theme === 'dark' 
                    ? 'bg-slate-700/50 text-slate-400' 
                    : 'bg-slate-100 text-slate-500'
                }`}
              >
                {systemHealth.config.models.llm} + {systemHealth.config.models.vision}
              </motion.div>
            )}

            {/* Theme Toggle */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onToggleTheme}
              className={`p-2 rounded-lg transition-all duration-200 ${
                theme === 'dark' 
                  ? 'bg-slate-800/50 hover:bg-slate-700/50 text-yellow-400' 
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              }`}
            >
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </motion.button>
          </div>
        </div>
        
        {/* Backend Connection Help */}
        {systemHealth?.status === 'unhealthy' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className={`mt-3 p-3 rounded-lg border ${
              theme === 'dark' 
                ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' 
                : 'bg-yellow-50 border-yellow-200 text-yellow-700'
            }`}
          >
            <div className="flex items-start space-x-2">
              <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="font-medium mb-1">Backend Server Required</p>
                <p className="text-xs opacity-90">
                  Start the backend: <code className="bg-black/20 px-1 rounded">cd backend && python main.py</code>
                </p>
                {systemHealth.backend_url && (
                  <p className="text-xs opacity-75 mt-1">
                    Trying to connect to: {systemHealth.backend_url}
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </motion.header>
  );
};

export default Header;