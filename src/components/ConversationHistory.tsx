import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { History, Search, Trash2, MessageSquare, Clock, User, Bot } from 'lucide-react';

interface ConversationHistoryProps {
  theme: 'light' | 'dark';
  userId: string | null;
  isVisible: boolean;
  onToggle: () => void;
  onSelectConversation: (sessionId: string) => void;
}

interface ConversationItem {
  session_id: string;
  timestamp: string;
  query: string;
  summary: string;
  message_count: number;
}

const ConversationHistory: React.FC<ConversationHistoryProps> = ({
  theme,
  userId,
  isVisible,
  onToggle,
  onSelectConversation
}) => {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredConversations, setFilteredConversations] = useState<ConversationItem[]>([]);

  // Mock data for demonstration
  useEffect(() => {
    if (userId) {
      const mockConversations: ConversationItem[] = [
        {
          session_id: 'session_1',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          query: 'Explain artificial intelligence',
          summary: 'Discussed AI fundamentals, machine learning, and applications',
          message_count: 5
        },
        {
          session_id: 'session_2',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          query: 'Compare Python and JavaScript',
          summary: 'Analyzed programming languages, use cases, and performance',
          message_count: 8
        },
        {
          session_id: 'session_3',
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          query: 'Climate change solutions',
          summary: 'Explored renewable energy, carbon capture, and policy measures',
          message_count: 12
        }
      ];
      setConversations(mockConversations);
    }
  }, [userId]);

  // Filter conversations based on search
  useEffect(() => {
    if (searchTerm) {
      const filtered = conversations.filter(conv =>
        conv.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
        conv.summary.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredConversations(filtered);
    } else {
      setFilteredConversations(conversations);
    }
  }, [conversations, searchTerm]);

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = Math.floor((now.getTime() - time.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return time.toLocaleDateString();
  };

  const deleteConversation = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setConversations(prev => prev.filter(conv => conv.session_id !== sessionId));
  };

  if (!isVisible) {
    return (
      <motion.button
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={onToggle}
        className={`fixed bottom-20 right-4 p-3 rounded-full shadow-lg z-40 ${
          theme === 'dark'
            ? 'bg-slate-800 hover:bg-slate-700 text-white border border-slate-700'
            : 'bg-white hover:bg-gray-50 text-slate-900 border border-gray-200'
        }`}
      >
        <History size={20} />
      </motion.button>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: '-100%' }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: '-100%' }}
      className={`fixed top-0 left-0 h-full w-80 shadow-2xl z-40 overflow-hidden ${
        theme === 'dark'
          ? 'bg-slate-900 border-r border-slate-700'
          : 'bg-white border-r border-gray-200'
      }`}
    >
      {/* Header */}
      <div className={`p-4 border-b ${
        theme === 'dark' ? 'border-slate-700' : 'border-gray-200'
      }`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <History size={20} className="text-blue-500" />
            <h3 className={`font-semibold ${
              theme === 'dark' ? 'text-white' : 'text-slate-900'
            }`}>
              Conversation History
            </h3>
          </div>
          
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
            ×
          </motion.button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search size={16} className={`absolute left-3 top-1/2 transform -translate-y-1/2 ${
            theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
          }`} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search conversations..."
            className={`w-full pl-9 pr-4 py-2 rounded-lg border text-sm ${
              theme === 'dark'
                ? 'bg-slate-800 border-slate-600 text-white placeholder-slate-400'
                : 'bg-white border-gray-300 text-slate-900 placeholder-slate-500'
            } focus:outline-none focus:ring-2 focus:ring-blue-500/20`}
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-3">
          {filteredConversations.map((conversation, index) => (
            <motion.div
              key={conversation.session_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => onSelectConversation(conversation.session_id)}
              className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-md ${
                theme === 'dark'
                  ? 'bg-slate-800 border-slate-700 hover:bg-slate-750'
                  : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <MessageSquare size={14} className="text-blue-500 mt-0.5" />
                  <h4 className={`text-sm font-medium line-clamp-1 ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    {conversation.query}
                  </h4>
                </div>
                
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={(e) => deleteConversation(conversation.session_id, e)}
                  className={`p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity ${
                    theme === 'dark' 
                      ? 'hover:bg-slate-600 text-slate-400' 
                      : 'hover:bg-gray-200 text-slate-500'
                  }`}
                >
                  <Trash2 size={12} />
                </motion.button>
              </div>
              
              <p className={`text-xs line-clamp-2 mb-2 ${
                theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
              }`}>
                {conversation.summary}
              </p>
              
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-1">
                  <Clock size={10} className={theme === 'dark' ? 'text-slate-500' : 'text-slate-400'} />
                  <span className={theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}>
                    {formatTimeAgo(conversation.timestamp)}
                  </span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <MessageSquare size={10} className={theme === 'dark' ? 'text-slate-500' : 'text-slate-400'} />
                  <span className={theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}>
                    {conversation.message_count}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
          
          {filteredConversations.length === 0 && (
            <div className={`text-center py-8 ${
              theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
            }`}>
              {searchTerm ? 'No conversations found' : 'No conversations yet'}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ConversationHistory;