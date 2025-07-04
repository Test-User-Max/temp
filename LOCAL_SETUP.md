# 🚀 Neurofluxion AI - Complete Local Setup Guide

## 📋 Prerequisites

Before starting, ensure you have the following installed on your system:

### Required Software
- **Python 3.9+** (Recommended: Python 3.10 or 3.11)
- **Node.js 18+** (Recommended: Node.js 18 LTS or 20 LTS)
- **Git** (for cloning the repository)
- **VS Code** or **Cursor IDE** (recommended)

### System Requirements
- **RAM**: Minimum 16GB (Recommended: 32GB for optimal performance)
- **Storage**: At least 20GB free space
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)

## 🔧 Step 1: Install Ollama and Models

### For Windows:
1. **Download Ollama:**
   - Visit [https://ollama.ai/](https://ollama.ai/)
   - Download the Windows installer
   - Run the installer and follow the setup wizard

2. **Install Required Models:**
   ```cmd
   # Open Command Prompt or PowerShell as Administrator
   ollama pull mistral
   ollama pull llava
   ollama pull phi
   ```

3. **Verify Installation:**
   ```cmd
   ollama list
   # Should show: mistral, llava, phi
   
   # Test Ollama server
   ollama serve
   ```

### For macOS:
1. **Install Ollama:**
   ```bash
   # Using Homebrew (recommended)
   brew install ollama
   
   # Or download from https://ollama.ai/
   ```

2. **Install Models:**
   ```bash
   ollama pull mistral
   ollama pull llava
   ollama pull phi
   ```

3. **Start Ollama Service:**
   ```bash
   # Start Ollama server
   ollama serve
   
   # In another terminal, verify
   curl http://localhost:11434/api/tags
   ```

### For Linux (Ubuntu/Debian):
1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Install Models:**
   ```bash
   ollama pull mistral
   ollama pull llava
   ollama pull phi
   ```

3. **Start as Service:**
   ```bash
   sudo systemctl enable ollama
   sudo systemctl start ollama
   
   # Verify
   curl http://localhost:11434/api/tags
   ```

## 📁 Step 2: Clone and Setup Project

### 1. Clone Repository:
```bash
# Clone the project
git clone <your-repository-url>
cd neurofluxion-ai

# Or if you have the files locally
cd path/to/neurofluxion-ai
```

### 2. Verify Project Structure:
```
neurofluxion-ai/
├── backend/
│   ├── agents/
│   ├── auth/
│   ├── core/
│   ├── debug/
│   ├── enhanced_memory/
│   ├── multilingual/
│   ├── plugins/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
├── src/
│   ├── components/
│   ├── hooks/
│   └── App.tsx
├── docker-compose.yml
├── package.json
└── LOCAL_SETUP.md
```

## 🐍 Step 3: Backend Setup

### 1. Navigate to Backend:
```bash
cd backend
```

### 2. Create Virtual Environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install System Dependencies:

**Windows:**
```cmd
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR

# Install FFmpeg
# Download from: https://ffmpeg.org/download.html
# Add to PATH

# Install Redis (optional)
# Download from: https://github.com/microsoftarchive/redis/releases
```

**macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install tesseract
brew install ffmpeg
brew install portaudio
brew install espeak
brew install redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    ffmpeg \
    portaudio19-dev \
    python3-pyaudio \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    build-essential \
    redis-server
```

### 4. Install Python Dependencies:
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# If you encounter issues, install key packages individually:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers sentence-transformers
pip install langchain langchain-community langgraph
pip install chromadb
pip install fastapi uvicorn
pip install whisper-openai
pip install pyttsx3 pyaudio
pip install Pillow pytesseract opencv-python
pip install PyPDF2 python-docx openpyxl
pip install redis PyJWT bcrypt passlib
```

### 5. Setup Environment Variables:
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

**Configure .env file:**
```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_VISION_MODEL=llava

# TTS Configuration
TTS_ENABLED=true
TTS_RATE=150
TTS_VOLUME=0.8

# STT Configuration
STT_ENABLED=true
WHISPER_MODEL=base

# Vector Store Configuration
CHROMA_PERSIST_DIR=./data/chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# General Configuration
LOG_LEVEL=INFO
MAX_TOKENS=2048
TEMPERATURE=0.7
SESSION_TIMEOUT=300

# File Upload Configuration
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# Memory Configuration
MEMORY_TYPE=file
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# OCR Configuration (Windows example)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 6. Create Required Directories:
```bash
mkdir -p data/chroma_db
mkdir -p data/memory
mkdir -p uploads
mkdir -p static/audio
mkdir -p plugins
```

### 7. Test Backend Dependencies:
```bash
# Test imports
python -c "
import fastapi, uvicorn, langchain, langgraph
import chromadb, sentence_transformers
import whisper, pyttsx3, pytesseract
from PIL import Image
import redis, jwt, bcrypt
print('✅ All backend dependencies installed successfully!')
"
```

## ⚛️ Step 4: Frontend Setup

### 1. Navigate to Project Root:
```bash
cd ..  # Go back to project root
```

### 2. Install Node.js Dependencies:
```bash
# Install dependencies
npm install

# If you encounter issues, try:
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### 3. Verify Frontend Dependencies:
```bash
npm list --depth=0
```

## 🚀 Step 5: Running the Application

### Method 1: Manual Startup (Recommended for Development)

**Terminal 1 - Start Ollama:**
```bash
# Make sure Ollama is running
ollama serve
```

**Terminal 2 - Start Redis (Optional):**
```bash
# Windows: Start Redis service or run redis-server.exe
# macOS: brew services start redis
# Linux: sudo systemctl start redis-server

# Or run Redis manually
redis-server
```

**Terminal 3 - Start Backend:**
```bash
cd backend

# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start FastAPI server
python main.py

# Alternative:
uvicorn main:app --reload --port 8000
```

**Terminal 4 - Start Frontend:**
```bash
# In project root
npm run dev
```

### Method 2: Using Docker (Production-Ready)

**Prerequisites:**
```bash
# Install Docker and Docker Compose
# Windows/macOS: Download Docker Desktop
# Linux: Install docker and docker-compose
```

**Start All Services:**
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🌐 Step 6: Access and Test the Application

### Application URLs:
- **Frontend**: http://localhost:5173 (dev) or http://localhost:3000 (docker)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Ollama API**: http://localhost:11434
- **Redis**: localhost:6379 (if running)

### Health Checks:
```bash
# Check backend health
curl http://localhost:8000/health

# Check Ollama
curl http://localhost:11434/api/tags

# Check if models are loaded
curl http://localhost:11434/api/show -d '{"name": "mistral"}'
```

## 🧪 Step 7: Testing All Features

### 1. User Authentication:
- Click "Sign In" in the header
- Register a new account
- Login with your credentials
- Verify user preferences are saved

### 2. Basic Text Query:
- Enter: "Explain artificial intelligence"
- Test with different languages
- Enable TTS and test audio output

### 3. Real-time Streaming:
- Enable "Streaming" toggle
- Submit a query and watch real-time output
- Test streaming interruption

### 4. Voice Input:
- Click "Voice Input" button
- Record a voice message
- Test speech-to-text functionality

### 5. Image Analysis:
- Upload an image file
- Enter: "What do you see in this image?"
- Test both vision analysis and OCR

### 6. Document Processing:
- Upload a PDF or DOCX file
- Enter: "Summarize this document"
- Check vector store integration

### 7. Multilingual Support:
- Change language using the language selector
- Submit queries in different languages
- Test translation functionality

### 8. Developer Debug Mode:
- Open developer panel (bottom right)
- Submit a query and watch debug logs
- Test performance metrics

### 9. Conversation History:
- Login and submit multiple queries
- Open conversation history panel
- Test conversation retrieval

### 10. Plugin System:
- Check `/plugins` endpoint
- Verify example plugin is loaded
- Test plugin functionality

## 🔧 Step 8: IDE Setup (VS Code/Cursor)

### 1. Open Project:
```bash
# For VS Code
code .

# For Cursor
cursor .
```

### 2. Install Recommended Extensions:
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **ES7+ React/Redux/React-Native snippets**
- **Tailwind CSS IntelliSense**
- **TypeScript Importer**
- **Auto Rename Tag**
- **Prettier**
- **ESLint**
- **Docker** (ms-azuretools.vscode-docker)

### 3. Configure Workspace Settings:
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "files.associations": {
    "*.css": "tailwindcss"
  }
}
```

## 🐛 Step 9: Troubleshooting

### Common Issues and Solutions:

#### 1. Ollama Connection Issues:
```bash
# Check if Ollama is running
ps aux | grep ollama  # Linux/macOS
tasklist | findstr ollama  # Windows

# Restart Ollama
pkill ollama  # Linux/macOS
ollama serve

# Check firewall settings
# Windows: Allow ollama.exe through Windows Firewall
# macOS: System Preferences > Security & Privacy > Firewall
# Linux: sudo ufw allow 11434
```

#### 2. Model Loading Issues:
```bash
# Check available models
ollama list

# Re-download models if corrupted
ollama rm mistral
ollama pull mistral

# Check model size and disk space
du -sh ~/.ollama/models/  # Linux/macOS
df -h
```

#### 3. Python Dependencies Issues:
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install with specific versions
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0

# For M1/M2 Macs
pip install torch torchvision torchaudio

# Clear pip cache
pip cache purge
```

#### 4. Audio/TTS Issues:
```bash
# Windows: Install Microsoft Visual C++ Redistributable
# macOS: Install Xcode command line tools
xcode-select --install

# Linux: Install additional audio libraries
sudo apt-get install pulseaudio pulseaudio-utils

# Test TTS manually
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Hello'); engine.runAndWait()"
```

#### 5. Redis Connection Issues:
```bash
# Check Redis status
redis-cli ping  # Should return PONG

# Start Redis
# Windows: redis-server.exe
# macOS: brew services start redis
# Linux: sudo systemctl start redis-server

# If Redis fails, the app will use fallback memory
```

#### 6. Authentication Issues:
```bash
# Check JWT secret in .env
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Clear browser storage if needed
# Open browser dev tools > Application > Storage > Clear
```

#### 7. Multilingual Model Issues:
```bash
# Download models manually if auto-download fails
python -c "
from transformers import AutoTokenizer, AutoModel
AutoTokenizer.from_pretrained('facebook/fasttext-language-identification')
AutoModel.from_pretrained('facebook/nllb-200-distilled-600M')
"
```

## 📊 Step 10: Performance Optimization

### 1. System Optimization:
```bash
# Increase virtual memory (Windows)
# System Properties > Advanced > Performance > Settings > Advanced > Virtual Memory

# Optimize for SSD (Linux)
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# macOS: Increase file descriptor limits
ulimit -n 65536
```

### 2. Model Optimization:
```env
# Use smaller models for faster inference
OLLAMA_MODEL=phi
WHISPER_MODEL=tiny

# Reduce token limits
MAX_TOKENS=1024
TEMPERATURE=0.5
```

### 3. Application Optimization:
```bash
# Enable production mode
NODE_ENV=production
npm run build
npm run preview

# Use Redis for better performance
MEMORY_TYPE=redis
REDIS_URL=redis://localhost:6379
```

## 🔄 Step 11: Development Workflow

### Daily Development:
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Redis (optional)
redis-server

# Terminal 3: Backend development
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py

# Terminal 4: Frontend development
npm run dev

# Terminal 5: Testing and debugging
curl http://localhost:8000/health
```

### Adding New Features:
1. **New Agents**: Create in `backend/agents/` and register in MCP
2. **New Plugins**: Add to `backend/plugins/` directory
3. **Frontend Components**: Add to `src/components/`
4. **API Endpoints**: Add to `backend/main.py`

### Testing:
```bash
# Backend API testing
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Test query", "language": "en"}'

# Frontend testing
npm run lint
npm run type-check
```

## 🚀 Step 12: Production Deployment

### Docker Production Setup:
```bash
# Create production docker-compose
cp docker-compose.yml docker-compose.prod.yml

# Edit for production
# - Remove volume mounts for source code
# - Add restart policies
# - Configure proper networking
# - Set up SSL/TLS

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production:
```env
# Production settings
LOG_LEVEL=WARNING
SESSION_TIMEOUT=1800
MAX_FILE_SIZE=52428800  # 50MB

# Security
JWT_SECRET_KEY=super-secure-production-key-256-bits-long
CORS_ORIGINS=["https://yourdomain.com"]

# Performance
MEMORY_TYPE=redis
REDIS_URL=redis://redis:6379
```

## ✅ Success Checklist

- [ ] Ollama installed and running with models (mistral, llava, phi)
- [ ] Python virtual environment created and activated
- [ ] All backend dependencies installed successfully
- [ ] Frontend dependencies installed
- [ ] Environment variables configured
- [ ] Required directories created
- [ ] Backend server running on port 8000
- [ ] Frontend running on port 5173
- [ ] Health check endpoint responding
- [ ] User authentication working
- [ ] Text query processed successfully
- [ ] Real-time streaming functional
- [ ] Voice input/output working
- [ ] Image upload and analysis working
- [ ] Document processing functional
- [ ] Multilingual support working
- [ ] Developer debug panel functional
- [ ] Conversation history working
- [ ] Plugin system operational
- [ ] All LangGraph agents functioning

## 🎯 Next Steps

Once you have the system running:

1. **Explore Features**: Test all the new production features
2. **Customize Agents**: Modify agent behavior and prompts
3. **Create Plugins**: Develop custom agents using the plugin system
4. **Add Languages**: Extend multilingual support
5. **Performance Tuning**: Optimize for your hardware
6. **Integration**: Connect with external APIs or databases
7. **Deployment**: Set up production environment
8. **Monitoring**: Implement logging and monitoring

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs**: Look at terminal outputs and log files
2. **Verify Prerequisites**: Ensure all software is properly installed
3. **Test Components**: Test each component individually
4. **Resource Monitoring**: Check system resources (RAM, CPU, disk)
5. **Debug Mode**: Use the developer panel for detailed debugging
6. **Community Support**: Check GitHub issues and discussions

## 🎉 Congratulations!

You now have a fully functional, production-ready Neurofluxion AI system with:

- ✅ Real-time streaming output
- ✅ User authentication & multi-user sessions
- ✅ Multilingual support (12 languages)
- ✅ Developer debug mode with comprehensive logging
- ✅ Plugin system for custom agents
- ✅ Enhanced memory with Redis support
- ✅ Voice input/output capabilities
- ✅ Multi-modal file processing
- ✅ Conversation history and user preferences
- ✅ Production-ready architecture

Your AI assistant is now ready for real-world use! 🚀