import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Copy, Share2, Volume2, Clock, Target, FileText, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface ResultDisplayProps {
  result: {
    query: string;
    intent: string;
    research: string;
    summary: string;
    key_points: string[];
    word_count: number;
    confidence: number;
    processing_time: number;
    steps: any[];
    audio?: {
      generated: boolean;
      file?: string;
      duration?: number;
    };
  };
  theme: 'light' | 'dark';
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, theme }) => {
  const [activeTab, setActiveTab] = useState<'summary' | 'research' | 'details'>('summary');
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioProgress, setAudioProgress] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  // Update audio URL when result.audio.file changes
  useEffect(() => {
    if (result.audio?.generated && result.audio.file) {
      let url = result.audio.file;
      console.log('DEBUG: result.audio.file =', url);
      if (url.startsWith('/audio/')) {
        url = `http://localhost:8000${url}`;
      }
      setAudioUrl(url);
      console.log('DEBUG: audioUrl set to', url);
      setIsPlaying(false);
      setAudioProgress(0);
    } else {
      setAudioUrl(null);
      setIsPlaying(false);
      setAudioProgress(0);
    }
  }, [result.audio?.file, result.audio?.generated]);

  // Handle play/pause
  const handlePlayPause = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
  };

  // Sync state with audio element
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onEnded = () => setIsPlaying(false);
    const onTimeUpdate = () => {
      setAudioProgress(audio.currentTime);
      setAudioDuration(audio.duration);
    };
    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('play', onPlay);
    audio.addEventListener('pause', onPause);
    return () => {
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('play', onPlay);
      audio.removeEventListener('pause', onPause);
    };
  }, [audioUrl]);

  // Seek
  const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (audioRef.current) {
      const newTime = Number(e.target.value);
      audioRef.current.currentTime = newTime;
      setAudioProgress(newTime);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const shareResult = async () => {
    if (navigator.share) {
      await navigator.share({
        title: 'AI Research Result',
        text: result.summary,
        url: window.location.href,
      });
    } else {
      copyToClipboard(result.summary);
    }
  };

  const tabs = [
    { id: 'summary', label: 'Summary', icon: FileText },
    { id: 'research', label: 'Full Research', icon: Target },
    { id: 'details', label: 'Details', icon: CheckCircle }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={`rounded-2xl backdrop-blur-md shadow-xl overflow-hidden border relative z-10 ${
        theme === 'dark' 
          ? 'bg-slate-800/40 border-slate-700/50' 
          : 'bg-white/70 border-slate-200/50'
      }`}
    >
      {/* Header */}
      <div className={`p-6 border-b ${
        theme === 'dark' ? 'border-slate-700/50' : 'border-slate-200/50'
      }`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className={`text-xl font-semibold ${
            theme === 'dark' ? 'text-white' : 'text-slate-900'
          }`}>
            Research Results
          </h3>
          
          <div className="flex items-center space-x-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => copyToClipboard(result.summary)}
              className={`p-2 rounded-lg transition-all duration-200 ${
                theme === 'dark' 
                  ? 'bg-slate-700/50 hover:bg-slate-600/50 text-slate-300' 
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              }`}
            >
              <Copy size={16} />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={shareResult}
              className={`p-2 rounded-lg transition-all duration-200 ${
                theme === 'dark' 
                  ? 'bg-slate-700/50 hover:bg-slate-600/50 text-slate-300' 
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              }`}
            >
              <Share2 size={16} />
            </motion.button>
            
            {result.audio?.generated && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handlePlayPause}
                className={`p-2 rounded-lg transition-all duration-200 ${
                  theme === 'dark' 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
                aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
              >
                {isPlaying ? <span style={{display:'inline-block',width:16}}>&#10073;&#10073;</span> : <Volume2 size={16} />}
              </motion.button>
            )}
          </div>
        </div>
        
        {/* Query Display */}
        <div className={`p-3 rounded-lg ${
          theme === 'dark' ? 'bg-slate-700/30' : 'bg-slate-50/50'
        }`}>
          <p className={`text-sm ${
            theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
          }`}>
            Query:
          </p>
          <p className={`font-medium ${
            theme === 'dark' ? 'text-white' : 'text-slate-900'
          }`}>
            {result.query}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className={`flex border-b ${
        theme === 'dark' ? 'border-slate-700/50' : 'border-slate-200/50'
      }`}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 p-4 text-center transition-all duration-200 ${
                activeTab === tab.id 
                  ? theme === 'dark' 
                    ? 'bg-blue-500/20 text-blue-400 border-b-2 border-blue-500' 
                    : 'bg-blue-50/80 text-blue-600 border-b-2 border-blue-500'
                  : theme === 'dark' 
                    ? 'text-slate-400 hover:text-slate-300' 
                    : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <Icon size={16} />
                <span className="text-sm font-medium">{tab.label}</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Hidden audio element for playback */}
        {audioUrl && (
          <audio
            key={audioUrl}
            ref={audioRef}
            src={audioUrl}
            preload="auto"
            style={{ display: 'none' }}
          />
        )}

        {/* Audio Controls */}
        {result.audio?.generated && result.audio.file && (
          <div className="mb-4 flex flex-col items-center">
            <input
              type="range"
              min={0}
              max={audioDuration || result.audio.duration || 0}
              value={audioProgress}
              onChange={handleProgressChange}
              step="0.01"
              className="w-full max-w-xs accent-blue-500"
              disabled={!audioDuration}
            />
            <div className="flex justify-between w-full max-w-xs text-xs mt-1">
              <span>{audioProgress.toFixed(1)}s</span>
              <span>{(audioDuration || result.audio.duration || 0).toFixed(1)}s</span>
            </div>
          </div>
        )}

        {activeTab === 'summary' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Summary */}
            <div>
              <h4 className={`text-lg font-semibold mb-3 ${
                theme === 'dark' ? 'text-white' : 'text-slate-900'
              }`}>
                Summary
              </h4>
              <div className={`p-4 rounded-lg ${
                theme === 'dark' ? 'bg-slate-700/30' : 'bg-slate-50/50'
              }`}>
                <p className={`leading-relaxed ${
                  theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                }`}>
                  {result.summary}
                </p>
              </div>
            </div>

            {/* Key Points */}
            {result.key_points.length > 0 && (
              <div>
                <h4 className={`text-lg font-semibold mb-3 ${
                  theme === 'dark' ? 'text-white' : 'text-slate-900'
                }`}>
                  Key Points
                </h4>
                <div className="space-y-2">
                  {result.key_points.map((point, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className={`flex items-start p-3 rounded-lg ${
                        theme === 'dark' ? 'bg-slate-700/30' : 'bg-slate-50/50'
                      }`}
                    >
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                      <p className={`text-sm ${
                        theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                      }`}>
                        {point}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'research' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h4 className={`text-lg font-semibold mb-3 ${
              theme === 'dark' ? 'text-white' : 'text-slate-900'
            }`}>
              Full Research Content
            </h4>
            <div className={`p-4 rounded-lg ${
              theme === 'dark' ? 'bg-slate-700/30' : 'bg-slate-50/50'
            }`}>
              <p className={`leading-relaxed whitespace-pre-wrap ${
                theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
              }`}>
                {result.research}
              </p>
            </div>
          </motion.div>
        )}

        {activeTab === 'details' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-lg ${
                theme === 'dark' ? 'bg-slate-700/30' : 'bg-slate-50/50'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  <Target size={16} className="text-blue-500" />
                  <span className={`text-sm font-medium ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    Intent
                  </span>
                </div>
                <p className={`text-sm ${
                  theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
                }`}>
                  {result.intent}
                </p>
              </div>

              <div className={`p-4 rounded-lg ${
                theme === 'dark' ? 'bg-slate-700/30' : 'bg-slate-50/50'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  <Clock size={16} className="text-green-500" />
                  <span className={`text-sm font-medium ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    Processing Time
                  </span>
                </div>
                <p className={`text-sm ${
                  theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
                }`}>
                  {result.processing_time.toFixed(2)}s
                </p>
              </div>

              <div className={`p-4 rounded-lg ${
                theme === 'dark' ? 'bg-slate-700/30' : 'bg-slate-50/50'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  <FileText size={16} className="text-purple-500" />
                  <span className={`text-sm font-medium ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    Word Count
                  </span>
                </div>
                <p className={`text-sm ${
                  theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
                }`}>
                  {result.word_count} words
                </p>
              </div>

              <div className={`p-4 rounded-lg ${
                theme === 'dark' ? 'bg-slate-700/30' : 'bg-slate-50/50'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle size={16} className="text-yellow-500" />
                  <span className={`text-sm font-medium ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    Confidence
                  </span>
                </div>
                <p className={`text-sm ${
                  theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
                }`}>
                  {(result.confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {result.audio?.generated && (
              <div className={`p-4 rounded-lg ${
                theme === 'dark' ? 'bg-blue-500/20' : 'bg-blue-50/80'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  <Volume2 size={16} className="text-blue-500" />
                  <span className={`text-sm font-medium ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    Audio Generated
                  </span>
                </div>
                <p className={`text-sm ${
                  theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
                }`}>
                  Duration: ~{result.audio.duration?.toFixed(1)}s
                </p>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default ResultDisplay;