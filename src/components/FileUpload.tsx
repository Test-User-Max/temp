import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, File, Image, Mic, X, CheckCircle } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onRemoveFile: () => void;
  selectedFile: File | null;
  theme: 'light' | 'dark';
  disabled?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ 
  onFileSelect, 
  onRemoveFile, 
  selectedFile, 
  theme, 
  disabled = false 
}) => {
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return <Image size={20} />;
    if (file.type.startsWith('audio/')) return <Mic size={20} />;
    return <File size={20} />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const supportedFormats = [
    'Images: PNG, JPG, JPEG, GIF, BMP',
    'Documents: PDF, DOCX, TXT',
    'Audio: WAV, MP3, M4A, FLAC'
  ];

  if (selectedFile) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`p-4 rounded-xl border-2 border-dashed ${
          theme === 'dark' 
            ? 'border-green-500/50 bg-green-500/10' 
            : 'border-green-500/50 bg-green-50'
        }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${
              theme === 'dark' ? 'bg-green-500/20 text-green-400' : 'bg-green-100 text-green-600'
            }`}>
              {getFileIcon(selectedFile)}
            </div>
            <div>
              <p className={`font-medium ${
                theme === 'dark' ? 'text-white' : 'text-slate-900'
              }`}>
                {selectedFile.name}
              </p>
              <p className={`text-sm ${
                theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
              }`}>
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <CheckCircle size={20} className="text-green-500" />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onRemoveFile}
              disabled={disabled}
              className={`p-1 rounded-lg transition-colors ${
                disabled 
                  ? 'opacity-50 cursor-not-allowed'
                  : theme === 'dark' 
                    ? 'hover:bg-red-500/20 text-red-400' 
                    : 'hover:bg-red-100 text-red-600'
              }`}
            >
              <X size={16} />
            </motion.button>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative p-6 rounded-xl border-2 border-dashed transition-all duration-200 cursor-pointer ${
        dragOver
          ? theme === 'dark'
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-blue-500 bg-blue-50'
          : theme === 'dark'
            ? 'border-slate-600 hover:border-slate-500'
            : 'border-slate-300 hover:border-slate-400'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => !disabled && fileInputRef.current?.click()}
    >
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileSelect}
        accept=".png,.jpg,.jpeg,.gif,.bmp,.pdf,.docx,.txt,.wav,.mp3,.m4a,.flac"
        className="hidden"
        disabled={disabled}
      />
      
      <div className="text-center">
        <motion.div
          animate={{ y: dragOver ? -5 : 0 }}
          className={`mx-auto w-12 h-12 rounded-xl mb-4 flex items-center justify-center ${
            theme === 'dark' ? 'bg-slate-700 text-slate-300' : 'bg-slate-100 text-slate-600'
          }`}
        >
          <Upload size={24} />
        </motion.div>
        
        <h3 className={`text-lg font-medium mb-2 ${
          theme === 'dark' ? 'text-white' : 'text-slate-900'
        }`}>
          Upload File
        </h3>
        
        <p className={`text-sm mb-4 ${
          theme === 'dark' ? 'text-slate-400' : 'text-slate-500'
        }`}>
          Drag and drop your file here, or click to browse
        </p>
        
        <div className="space-y-1">
          {supportedFormats.map((format, index) => (
            <p key={index} className={`text-xs ${
              theme === 'dark' ? 'text-slate-500' : 'text-slate-400'
            }`}>
              {format}
            </p>
          ))}
        </div>
        
        <p className={`text-xs mt-2 ${
          theme === 'dark' ? 'text-slate-500' : 'text-slate-400'
        }`}>
          Maximum file size: 10MB
        </p>
      </div>
    </motion.div>
  );
};

export default FileUpload;