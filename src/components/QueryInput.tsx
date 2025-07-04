import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Mic, MicOff, Loader2, Upload, AlertCircle } from 'lucide-react';
import FileUpload from './FileUpload';

interface QueryInputProps {
  onSubmit: (query: string, enableTts: boolean, file?: File) => void;
  loading: boolean;
  theme: 'light' | 'dark';
  disabled?: boolean;
}

const QueryInput: React.FC<QueryInputProps> = ({ onSubmit, loading, theme, disabled = false }) => {
  const [query, setQuery] = useState('');
  const [enableTts, setEnableTts] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((query.trim() || selectedFile) && !loading && !disabled) {
      onSubmit(query.trim() || 'Analyze this file', enableTts, selectedFile || undefined);
      setQuery('');
      setSelectedFile(null);
      setShowFileUpload(false);
    }
  };

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setShowFileUpload(false);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
  };

  const exampleQueries = [
    "Summarize India's 2030 climate goals",
    "Compare GPT-4 and Mixtral models",
    "Explain quantum computing principles",
    "Research renewable energy trends",
    "Analyze this image content",
    "Extract text from document"
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className={`rounded-2xl p-6 backdrop-blur-md shadow-xl border relative z-10 ${
        disabled 
          ? theme === 'dark' 
            ? 'bg-slate-800/20 border-slate-700/30 opacity-60' 
            : 'bg-white/40 border-slate-200/30 opacity-60'
          : theme === 'dark' 
            ? 'bg-slate-800/40 border-slate-700/50' 
            : 'bg-white/70 border-slate-200/50'
      }`}
    >
      {/* Disabled State Warning */}
      {disabled && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mb-4 p-3 rounded-lg border ${
            theme === 'dark' 
              ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' 
              : 'bg-yellow-50 border-yellow-200 text-yellow-700'
          }`}
        >
          <div className="flex items-center space-x-2">
            <AlertCircle size={16} />
            <span className="text-sm font-medium">Backend Connection Required</span>
          </div>
          <p className="text-xs mt-1 opacity-90">
            Start the backend server to begin using Neurofluxion AI
          </p>
        </motion.div>
      )}

      {/* File Upload Section */}
      {showFileUpload && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="mb-6"
        >
          <FileUpload
            onFileSelect={handleFileSelect}
            onRemoveFile={handleRemoveFile}
            selectedFile={selectedFile}
            theme={theme}
            disabled={loading || disabled}
          />
        </motion.div>
      )}

      {/* Selected File Display */}
      {selectedFile && !showFileUpload && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <FileUpload
            onFileSelect={handleFileSelect}
            onRemoveFile={handleRemoveFile}
            selectedFile={selectedFile}
            theme={theme}
            disabled={loading || disabled}
          />
        </motion.div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Query Input */}
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              disabled 
                ? "Start the backend server to use Neurofluxion AI..."
                : selectedFile 
                  ? "Describe what you want to know about this file..." 
                  : "Ask anything... I'll orchestrate intelligence across voice, vision, and thought!"
            }
            disabled={loading || disabled}
            className={`w-full px-4 py-3 pr-12 rounded-xl resize-none transition-all duration-200 ${
              disabled
                ? theme === 'dark' 
                  ? 'bg-slate-700/30 border-slate-600/50 text-slate-500 placeholder-slate-600 cursor-not-allowed' 
                  : 'bg-white/50 border-slate-200/50 text-slate-400 placeholder-slate-400 cursor-not-allowed'
                : theme === 'dark' 
                  ? 'bg-slate-700/50 border-slate-600 text-white placeholder-slate-400 focus:border-cyan-500' 
                  : 'bg-white/80 border-slate-200 text-slate-900 placeholder-slate-500 focus:border-cyan-500'
            } border-2 focus:outline-none focus:ring-2 focus:ring-cyan-500/20`}
            rows={selectedFile ? 2 : 3}
          />
          
          <motion.button
            type="submit"
            disabled={(!query.trim() && !selectedFile) || loading || disabled}
            whileHover={!disabled ? { scale: 1.05 } : {}}
            whileTap={!disabled ? { scale: 0.95 } : {}}
            className={`absolute bottom-3 right-3 p-2 rounded-lg transition-all duration-200 ${
              (query.trim() || selectedFile) && !loading && !disabled
                ? 'bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white'
                : theme === 'dark' 
                  ? 'bg-slate-600 text-slate-400' 
                  : 'bg-slate-200 text-slate-500'
            } disabled:cursor-not-allowed`}
          >
            {loading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </motion.button>
        </div>

        {/* Options */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <motion.button
              type="button"
              onClick={() => !disabled && setEnableTts(!enableTts)}
              whileHover={!disabled ? { scale: 1.02 } : {}}
              whileTap={!disabled ? { scale: 0.98 } : {}}
              disabled={disabled}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                disabled
                  ? theme === 'dark' 
                    ? 'bg-slate-700/30 text-slate-500 cursor-not-allowed' 
                    : 'bg-slate-100/50 text-slate-400 cursor-not-allowed'
                  : enableTts 
                    ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white' 
                    : theme === 'dark' 
                      ? 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50' 
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {enableTts ? <Mic size={16} /> : <MicOff size={16} />}
              <span className="text-sm">Text-to-Speech</span>
            </motion.button>
            
            <motion.button
              type="button"
              onClick={() => !disabled && setShowFileUpload(!showFileUpload)}
              whileHover={!disabled ? { scale: 1.02 } : {}}
              whileTap={!disabled ? { scale: 0.98 } : {}}
              disabled={disabled}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                disabled
                  ? theme === 'dark' 
                    ? 'bg-slate-700/30 text-slate-500 cursor-not-allowed' 
                    : 'bg-slate-100/50 text-slate-400 cursor-not-allowed'
                  : showFileUpload || selectedFile
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white' 
                    : theme === 'dark' 
                      ? 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50' 
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Upload size={16} />
              <span className="text-sm">Upload File</span>
            </motion.button>
          </div>
          
          <div className={`text-sm ${
            theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
          }`}>
            {query.length}/2000
          </div>
        </div>
      </form>

      {/* Example Queries */}
      {!selectedFile && !disabled && (
        <div className="mt-6">
          <p className={`text-sm mb-3 ${
            theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
          }`}>
            Try these examples:
          </p>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((example, index) => (
              <motion.button
                key={index}
                onClick={() => setQuery(example)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`px-3 py-1 rounded-full text-sm transition-all duration-200 ${
                  theme === 'dark' 
                    ? 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50 border border-slate-600/50' 
                    : 'bg-slate-100/80 text-slate-600 hover:bg-slate-200/80 border border-slate-200'
                }`}
              >
                {example}
              </motion.button>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default QueryInput;