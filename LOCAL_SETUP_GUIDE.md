# 🚀 MCP-Driven Multi-Agent AI Assistant - Local Setup Guide

## 📋 Prerequisites

Before starting, ensure you have the following installed on your system:

### Required Software
- **Python 3.8+** (Recommended: Python 3.9 or 3.10)
- **Node.js 16+** (Recommended: Node.js 18 LTS)
- **Git** (for cloning the repository)
- **VS Code** or **Cursor IDE**

### System Requirements
- **RAM**: Minimum 8GB (Recommended: 16GB)
- **Storage**: At least 10GB free space
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)

## 🔧 Step 1: Install Ollama and Mistral Model

### For Windows:
1. **Download Ollama:**
   - Visit [https://ollama.ai/](https://ollama.ai/)
   - Download the Windows installer
   - Run the installer and follow the setup wizard

2. **Install Mistral Model:**
   ```cmd
   # Open Command Prompt or PowerShell
   ollama pull mistral
   ```

3. **Verify Installation:**
   ```cmd
   ollama list
   # Should show mistral in the list
   ```

### For macOS:
1. **Install Ollama:**
   ```bash
   # Using Homebrew (recommended)
   brew install ollama
   
   # Or download from https://ollama.ai/
   ```

2. **Install Mistral Model:**
   ```bash
   ollama pull mistral
   ```

3. **Start Ollama Service:**
   ```bash
   ollama serve
   ```

### For Linux (Ubuntu/Debian):
1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Install Mistral Model:**
   ```bash
   ollama pull mistral
   ```

3. **Start Ollama Service:**
   ```bash
   ollama serve
   ```

### Verify Ollama is Running:
```bash
# Test Ollama connection
curl http://localhost:11434/api/tags
# Should return JSON with available models
```

## 📁 Step 2: Clone and Setup the Project

### 1. Clone the Repository:
```bash
# Clone the project (replace with actual repository URL)
git clone <repository-url>
cd mcp-ai-assistant

# Or if you have the project files locally, navigate to the project directory
cd path/to/mcp-ai-assistant
```

### 2. Project Structure Verification:
Ensure your project structure looks like this:
```
mcp-ai-assistant/
├── backend/
│   ├── agents/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
├── src/
│   ├── components/
│   ├── hooks/
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── README.md
└── ...
```

## 🐍 Step 3: Backend Setup

### 1. Navigate to Backend Directory:
```bash
cd backend
```

### 2. Create Python Virtual Environment:

**For Windows:**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**For macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Python Dependencies:
```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### 4. Setup Environment Variables:
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your preferred settings
```

**Edit `.env` file:**
```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral

# TTS Configuration
TTS_ENABLED=true
TTS_RATE=150
TTS_VOLUME=0.8

# General Configuration
LOG_LEVEL=INFO
MAX_TOKENS=2048
TEMPERATURE=0.7
SESSION_TIMEOUT=300
```

### 5. Test Backend Dependencies:
```bash
# Test if all imports work
python -c "import fastapi, uvicorn, pyttsx3, aiohttp; print('All dependencies installed successfully!')"
```

## ⚛️ Step 4: Frontend Setup

### 1. Navigate to Project Root:
```bash
# Go back to project root
cd ..
```

### 2. Install Node.js Dependencies:
```bash
# Install all frontend dependencies
npm install
```

### 3. Verify Frontend Dependencies:
```bash
# Check if installation was successful
npm list --depth=0
```

## 🚀 Step 5: Running the Application

### Method 1: Using Separate Terminals

**Terminal 1 - Start Ollama (if not already running):**
```bash
ollama serve
```

**Terminal 2 - Start Backend:**
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start FastAPI server
python main.py

# Alternative method:
# uvicorn main:app --reload --port 8000
```

**Terminal 3 - Start Frontend:**
```bash
# In project root directory
npm run dev
```

### Method 2: Using Package.json Scripts

**Start Backend:**
```bash
npm run backend
```

**Start Frontend (in another terminal):**
```bash
npm run dev
```

## 🌐 Step 6: Access the Application

Once all services are running:

1. **Frontend**: Open [http://localhost:5173](http://localhost:5173)
2. **Backend API**: [http://localhost:8000](http://localhost:8000)
3. **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
4. **Ollama API**: [http://localhost:11434](http://localhost:11434)

## 🔧 Step 7: VS Code/Cursor IDE Setup

### 1. Open Project in IDE:
```bash
# For VS Code
code .

# For Cursor
cursor .
```

### 2. Recommended VS Code Extensions:
Install these extensions for better development experience:

- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **ES7+ React/Redux/React-Native snippets** (dsznajder.es7-react-js-snippets)
- **Tailwind CSS IntelliSense** (bradlc.vscode-tailwindcss)
- **TypeScript Importer** (pmneo.tsimporter)
- **Auto Rename Tag** (formulahendry.auto-rename-tag)
- **Prettier** (esbenp.prettier-vscode)
- **ESLint** (dbaeumer.vscode-eslint)

### 3. VS Code Workspace Settings:
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

### 4. Launch Configuration:
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
    }
  ]
}
```

## 🧪 Step 8: Testing the Setup

### 1. Health Check:
Visit [http://localhost:8000/health](http://localhost:8000/health) - should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX..."
}
```

### 2. Test Query:
1. Open the frontend at [http://localhost:5173](http://localhost:5173)
2. Enter a test query: "Explain artificial intelligence"
3. Click submit and watch the agent pipeline process your request

### 3. Test API Directly:
```bash
# Test the API endpoint
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "enable_tts": false
  }'
```

## 🐛 Troubleshooting

### Common Issues and Solutions:

#### 1. Ollama Connection Failed
**Error**: `Connection refused to localhost:11434`

**Solutions:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# Check if Mistral model is installed
ollama list
```

#### 2. Python Import Errors
**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions:**
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. TTS Not Working
**Error**: TTS agent fails to initialize

**Solutions:**
```bash
# Install system TTS dependencies

# Windows: Usually works out of the box

# macOS:
brew install espeak

# Linux (Ubuntu/Debian):
sudo apt-get install espeak espeak-data libespeak1 libespeak-dev

# Disable TTS if issues persist
# In .env file: TTS_ENABLED=false
```

#### 4. Frontend Build Errors
**Error**: `Module not found` or TypeScript errors

**Solutions:**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear npm cache
npm cache clean --force
```

#### 5. Port Already in Use
**Error**: `Port 8000 is already in use`

**Solutions:**
```bash
# Find and kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --reload --port 8001
```

#### 6. Memory Issues with Mistral
**Error**: System runs out of memory

**Solutions:**
```bash
# Use smaller model
ollama pull phi

# Update .env file:
OLLAMA_MODEL=phi

# Reduce token limits
MAX_TOKENS=1024
```

## 📊 Performance Optimization

### 1. System Optimization:
```bash
# Monitor system resources
# Windows: Task Manager
# macOS: Activity Monitor
# Linux: htop or top
```

### 2. Backend Optimization:
```python
# In config.py, adjust these settings for your system:
MAX_TOKENS=1024  # Reduce for faster responses
TEMPERATURE=0.5  # Lower for more focused responses
```

### 3. Frontend Optimization:
```bash
# Build optimized version for production
npm run build
npm run preview
```

## 🔄 Development Workflow

### 1. Daily Development:
```bash
# Start development environment
# Terminal 1: ollama serve
# Terminal 2: cd backend && source venv/bin/activate && python main.py
# Terminal 3: npm run dev
```

### 2. Making Changes:
- **Backend changes**: Server auto-reloads with `--reload` flag
- **Frontend changes**: Vite hot-reloads automatically
- **Environment changes**: Restart backend server

### 3. Adding New Agents:
1. Create new agent class in `backend/agents/`
2. Register agent in `mcp.py`
3. Update frontend if needed
4. Test with sample queries

## 📚 Additional Resources

### Documentation:
- **FastAPI**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **React**: [https://react.dev/](https://react.dev/)
- **Tailwind CSS**: [https://tailwindcss.com/](https://tailwindcss.com/)
- **Ollama**: [https://ollama.ai/](https://ollama.ai/)

### Useful Commands:
```bash
# Backend commands
pip freeze > requirements.txt  # Update requirements
python -m pytest  # Run tests (if added)

# Frontend commands
npm run build  # Build for production
npm run lint   # Check code quality
npm run preview  # Preview production build

# Ollama commands
ollama list  # List installed models
ollama rm mistral  # Remove model
ollama pull llama2  # Install different model
```

## 🎯 Next Steps

Once you have the system running:

1. **Experiment with Queries**: Try different types of questions
2. **Customize Agents**: Modify agent behavior in the backend
3. **Enhance UI**: Add new features to the frontend
4. **Performance Tuning**: Optimize for your hardware
5. **Add New Models**: Experiment with different Ollama models

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs**: Look at terminal outputs for error messages
2. **Verify Prerequisites**: Ensure all required software is installed
3. **Test Components**: Test each component (Ollama, Backend, Frontend) separately
4. **Resource Monitoring**: Check if system has enough memory/CPU
5. **Documentation**: Refer to the technical documentation in `TECHNICAL_QA.md`

## ✅ Success Checklist

- [ ] Ollama installed and running
- [ ] Mistral model downloaded
- [ ] Python virtual environment created and activated
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Environment variables configured
- [ ] Backend server running on port 8000
- [ ] Frontend running on port 5173
- [ ] Health check endpoint responding
- [ ] Test query processed successfully
- [ ] All agent pipeline steps working
- [ ] TTS functionality working (if enabled)

Congratulations! You now have a fully functional MCP-Driven Multi-Agent AI Assistant running locally on your system.