# 🚀 Complete MCP-Driven Multi-Modal AI Assistant Setup Guide

## 📋 System Requirements

### Hardware Requirements
- **RAM**: Minimum 16GB (Recommended: 32GB)
- **Storage**: At least 20GB free space
- **CPU**: Multi-core processor (Intel i5/AMD Ryzen 5 or better)
- **GPU**: Optional but recommended for faster inference

### Software Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **Node.js**: 18 LTS or higher
- **Git**: Latest version
- **Docker**: Latest version (optional but recommended)

## 🔧 Step 1: Install Ollama and Models

### For Windows:
1. **Download and Install Ollama:**
   ```cmd
   # Download from https://ollama.ai/
   # Run the installer and follow setup wizard
   ```

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
cd mcp-ai-assistant

# Or if you have the files locally
cd path/to/mcp-ai-assistant
```

### 2. Verify Project Structure:
```
mcp-ai-assistant/
├── backend/
│   ├── agents/
│   ├── core/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
├── src/
│   ├── components/
│   ├── hooks/
│   └── App.tsx
├── docker-compose.yml
├── package.json
└── COMPLETE_SETUP_GUIDE.md
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
    build-essential
```

### 4. Install Python Dependencies:
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# If you encounter issues, install individually:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers sentence-transformers
pip install langchain langchain-community langgraph
pip install chromadb
pip install fastapi uvicorn
pip install whisper-openai
pip install pyttsx3 pyaudio
pip install Pillow pytesseract opencv-python
pip install PyPDF2 python-docx openpyxl
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

# OCR Configuration (Windows example)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 6. Create Required Directories:
```bash
mkdir -p data/chroma_db
mkdir -p data/memory
mkdir -p uploads
mkdir -p static/audio
```

### 7. Test Backend Dependencies:
```bash
# Test imports
python -c "
import fastapi, uvicorn, langchain, langgraph
import chromadb, sentence_transformers
import whisper, pyttsx3, pytesseract
from PIL import Image
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

**Terminal 2 - Start Backend:**
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

**Terminal 3 - Start Frontend:**
```bash
# In project root
npm run dev
```

### Method 2: Using Docker (Recommended for Production)

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

**Individual Service Management:**
```bash
# Start only specific services
docker-compose up ollama chromadb redis

# Scale services
docker-compose up --scale backend=2

# Rebuild specific service
docker-compose build backend
docker-compose up backend
```

## 🌐 Step 6: Access and Test the Application

### Application URLs:
- **Frontend**: http://localhost:5173 (dev) or http://localhost:3000 (docker)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Ollama API**: http://localhost:11434
- **ChromaDB**: http://localhost:8001 (if using docker)

### Health Checks:
```bash
# Check backend health
curl http://localhost:8000/health

# Check Ollama
curl http://localhost:11434/api/tags

# Check if models are loaded
curl http://localhost:11434/api/show -d '{"name": "mistral"}'
```

## 🧪 Step 7: Testing the System

### 1. Basic Text Query:
- Open frontend at http://localhost:5173
- Enter: "Explain artificial intelligence"
- Click submit and watch the LangGraph pipeline

### 2. Image Analysis:
- Upload an image file
- Enter: "What do you see in this image?"
- Test both vision analysis and OCR

### 3. Document Processing:
- Upload a PDF or DOCX file
- Enter: "Summarize this document"
- Check vector store integration

### 4. Audio Processing:
- Upload an audio file (WAV, MP3)
- Enter: "Transcribe this audio"
- Test speech-to-text functionality

### 5. Text-to-Speech:
- Enable TTS toggle
- Submit any text query
- Check if audio is generated

### 6. API Testing:
```bash
# Test text query
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "enable_tts": false
  }'

# Test file upload
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/file.pdf" \
  -F "query=Summarize this document" \
  -F "enable_tts=false"
```

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
  },
  "docker.defaultRegistryPath": "localhost:5000"
}
```

### 4. Debug Configuration:
Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/main.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Docker: Backend",
      "type": "docker",
      "request": "launch",
      "preLaunchTask": "docker-run: debug",
      "python": {
        "pathMappings": [
          {
            "localRoot": "${workspaceFolder}/backend",
            "remoteRoot": "/app"
          }
        ],
        "projectType": "fastapi"
      }
    }
  ]
}
```

## 🐛 Step 9: Troubleshooting

### Common Issues and Solutions:

#### 1. Ollama Connection Issues:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
pkill ollama
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
du -sh ~/.ollama/models/
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

#### 5. OCR/Tesseract Issues:
```bash
# Verify Tesseract installation
tesseract --version

# Test OCR
tesseract test_image.png output.txt

# Windows: Add to PATH
set PATH=%PATH%;C:\Program Files\Tesseract-OCR

# Update .env with correct path
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

#### 6. Memory Issues:
```bash
# Monitor memory usage
# Windows: Task Manager
# macOS: Activity Monitor
# Linux: htop or free -h

# Reduce model size
ollama pull phi  # Smaller model
# Update .env: OLLAMA_MODEL=phi

# Adjust token limits
MAX_TOKENS=1024
```

#### 7. Port Conflicts:
```bash
# Check what's using ports
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000

# Kill processes using ports
# Windows: taskkill /PID <PID> /F
# macOS/Linux: kill -9 <PID>

# Use different ports
uvicorn main:app --port 8001
npm run dev -- --port 5174
```

#### 8. Docker Issues:
```bash
# Check Docker status
docker --version
docker-compose --version

# Clean Docker cache
docker system prune -a

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up

# Check container logs
docker-compose logs backend
docker-compose logs ollama
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

# Use Redis for session management
MEMORY_TYPE=redis
REDIS_URL=redis://localhost:6379
```

## 🔄 Step 11: Development Workflow

### Daily Development:
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Backend development
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py

# Terminal 3: Frontend development
npm run dev

# Terminal 4: Testing and debugging
curl http://localhost:8000/health
```

### Adding New Agents:
1. Create agent class in `backend/agents/`
2. Register in `backend/core/langgraph_mcp.py`
3. Update frontend components if needed
4. Test with sample queries

### Database Management:
```bash
# Check vector store stats
curl http://localhost:8000/stats

# Add documents to vector store
curl -X POST "http://localhost:8000/documents/add" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/document.pdf"}'

# Search documents
curl "http://localhost:8000/documents/search?query=machine%20learning"
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
CORS_ORIGINS=["https://yourdomain.com"]
API_KEYS_ENABLED=true
```

## 📚 Step 13: Additional Resources

### Documentation:
- **LangChain**: https://python.langchain.com/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Ollama**: https://ollama.ai/
- **ChromaDB**: https://docs.trychroma.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/

### Useful Commands:
```bash
# Backend commands
pip freeze > requirements.txt
python -m pytest  # Run tests (if added)
black .  # Code formatting
flake8 .  # Linting

# Frontend commands
npm run build  # Production build
npm run lint   # ESLint
npm run type-check  # TypeScript checking

# Docker commands
docker-compose logs -f backend
docker-compose exec backend bash
docker-compose restart ollama

# Ollama commands
ollama list  # List models
ollama show mistral  # Model info
ollama rm model_name  # Remove model
ollama cp mistral my-custom-model  # Copy model
```

## ✅ Success Checklist

- [ ] Ollama installed and running
- [ ] Models downloaded (mistral, llava, phi)
- [ ] Python virtual environment created
- [ ] All backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Environment variables configured
- [ ] Required directories created
- [ ] Backend server running on port 8000
- [ ] Frontend running on port 5173
- [ ] Health check endpoint responding
- [ ] Text query processed successfully
- [ ] Image upload and analysis working
- [ ] Document processing functional
- [ ] Audio transcription working
- [ ] TTS functionality working
- [ ] Vector store integration working
- [ ] All LangGraph agents functioning
- [ ] Docker setup working (optional)

## 🎯 Next Steps

Once you have the system running:

1. **Experiment with Queries**: Try different types of inputs
2. **Customize Agents**: Modify agent behavior and prompts
3. **Add Custom Models**: Experiment with different Ollama models
4. **Enhance UI**: Add new features to the frontend
5. **Performance Tuning**: Optimize for your hardware
6. **Integration**: Connect with external APIs or databases
7. **Deployment**: Set up production environment

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs**: Look at terminal outputs and log files
2. **Verify Prerequisites**: Ensure all software is properly installed
3. **Test Components**: Test each component individually
4. **Resource Monitoring**: Check system resources (RAM, CPU, disk)
5. **Community Support**: Check GitHub issues and discussions

Congratulations! You now have a fully functional LangGraph-driven Multi-Modal AI Assistant with comprehensive capabilities including text, image, audio, and document processing.