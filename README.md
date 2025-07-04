# Neurofluxion AI

**Orchestrating Intelligence — Across Voice, Vision, and Thought**

A sophisticated multi-agent AI assistant system powered by LangGraph orchestration that coordinates multiple autonomous agents using only open-source LLMs via Ollama. Built with FastAPI backend and React frontend featuring premium UI/UX with glassmorphism effects and smooth animations.

## 🚀 Features

### Core Functionality
- **LangGraph Orchestration**: Intelligent agent routing with conditional workflows and quality control loops
- **Multi-Agent Control Plane (MCP)**: Coordinates agent flow based on query intent and input type
- **Multi-Modal Processing**: Supports text, images, audio, and document inputs
- **Local AI Processing**: Fully offline using Mistral, LLaVA, and Whisper models via Ollama
- **Vector Database**: ChromaDB integration for document retrieval and context awareness
- **Memory Management**: Persistent session context and conversation history

### Specialized Agents
- **IntentAgent**: Advanced intent classification using LLM
- **ResearchAgent**: Comprehensive research using local Mistral model
- **CompareAgent**: Dedicated comparison analysis
- **SummarizerAgent**: Intelligent summarization with key point extraction
- **RetrieverAgent**: Vector search and document retrieval
- **VisionAgent**: Image analysis using LLaVA model
- **OCRAgent**: Text extraction from images using Tesseract
- **STTAgent**: Speech-to-text using Whisper
- **TTSAgent**: Text-to-speech with quality voice synthesis
- **CritiqueAgent**: Quality control and response evaluation

### Technical Stack
- **Backend**: FastAPI with async agent processing
- **Frontend**: React with TypeScript and Tailwind CSS
- **Orchestration**: LangGraph for intelligent workflow management
- **LLM**: Mistral, LLaVA via Ollama (fully local, no API keys required)
- **Vector Store**: ChromaDB for document embeddings
- **Animation**: Framer Motion for smooth transitions
- **Audio**: Offline text-to-speech and speech recognition

### UI/UX Features
- **Premium Design**: Glassmorphism and neumorphism effects
- **Dark/Light Theme**: Elegant color schemes with smooth transitions
- **Real-time Progress**: Animated LangGraph pipeline visualization
- **Multi-Modal Input**: Drag & drop file upload with preview
- **Responsive Design**: Mobile-first approach with elegant typography
- **Interactive Elements**: Hover states and micro-interactions

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- [Ollama](https://ollama.ai/) installed and running
- 16GB+ RAM recommended

### 1. Install Ollama and Models
```bash
# Install Ollama (visit https://ollama.ai/ for instructions)
# Then pull the required models
ollama pull mistral
ollama pull llava
ollama serve
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Start the backend server
python main.py
```

### 3. Frontend Setup
```bash
# Install frontend dependencies
npm install

# Start the development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
neurofluxion-ai/
├── backend/
│   ├── agents/
│   │   ├── langchain_agents.py      # LangChain-based agents
│   │   ├── multimodal_agents.py     # Vision, OCR, STT, TTS agents
│   │   └── __init__.py
│   ├── core/
│   │   ├── langgraph_mcp.py         # LangGraph orchestration
│   │   ├── llm_interface.py         # Ollama LLM integration
│   │   ├── vectorstore.py           # ChromaDB integration
│   │   ├── memory.py                # Session management
│   │   └── embeddings.py            # Embedding service
│   ├── main.py                      # FastAPI application
│   ├── config.py                    # Configuration management
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                 # Environment template
├── src/
│   ├── components/
│   │   ├── Header.tsx               # App header with status
│   │   ├── QueryInput.tsx           # Multi-modal input interface
│   │   ├── AgentProgress.tsx        # LangGraph pipeline visualization
│   │   ├── ResultDisplay.tsx        # Results with audio playback
│   │   ├── FileUpload.tsx           # Drag & drop file upload
│   │   └── Footer.tsx               # App footer
│   ├── hooks/
│   │   ├── useTheme.ts              # Theme management
│   │   └── useApi.ts                # API integration
│   ├── App.tsx                      # Main application
│   ├── App.css                      # Custom styles
│   └── main.tsx                     # React entry point
├── docker-compose.yml               # Docker orchestration
├── package.json                     # Node.js dependencies
└── README.md                        # This file
```

## 🎯 Usage Examples

### Basic Research Query
```
"Summarize India's 2030 climate goals"
```
**Agent Flow**: IntentAgent → ResearchAgent → SummarizerAgent → Result Display

### Comparison Query
```
"Compare GPT-4 and Mixtral models"
```
**Agent Flow**: IntentAgent → CompareAgent → SummarizerAgent → Result Display

### Image Analysis
```
Upload an image + "What do you see in this image?"
```
**Agent Flow**: VisionAgent → SummarizerAgent → Result Display

### Document Processing
```
Upload PDF + "Summarize this document"
```
**Agent Flow**: DocumentProcessor → RetrieverAgent → SummarizerAgent → Result Display

### Voice-Enabled Query
```
"Explain quantum computing" (with TTS enabled)
```
**Agent Flow**: IntentAgent → ResearchAgent → SummarizerAgent → TTSAgent → Audio Output

## 🔧 Configuration

### Environment Variables (.env)
```bash
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
```

### Customizing Agents
Each agent can be customized by modifying the respective files in `backend/agents/`:
- **LangChain Agents**: Modify prompts and behavior in `langchain_agents.py`
- **Multimodal Agents**: Adjust processing logic in `multimodal_agents.py`
- **LangGraph Flow**: Customize orchestration in `core/langgraph_mcp.py`

## 🌟 Key Features

### LangGraph Orchestration
The system uses LangGraph for intelligent agent coordination:
1. **Conditional Routing**: Routes based on intent and input type
2. **Quality Control**: Critique agent with retry loops
3. **Parallel Processing**: Concurrent execution where possible
4. **State Management**: Comprehensive workflow state tracking

### Multi-Modal Capabilities
- **Text Processing**: Advanced research and analysis
- **Image Analysis**: LLaVA vision model integration
- **Audio Processing**: Whisper speech-to-text
- **Document Processing**: PDF, DOCX, TXT with chunking
- **Voice Output**: High-quality text-to-speech

### Premium UI/UX
- **Glassmorphism Effects**: Translucent elements with backdrop blur
- **Smooth Animations**: Framer Motion for fluid transitions
- **Responsive Design**: Optimized for all screen sizes
- **Dark/Light Themes**: Professional color schemes with high contrast
- **Interactive Feedback**: Visual feedback for all user interactions

## 🚀 Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Production Deployment
```bash
# Build frontend
npm run build

# Start backend in production mode
cd backend && python main.py
```

## 🔍 API Endpoints

### Core Endpoints
- `POST /ask` - Submit text query for processing
- `POST /upload` - Upload and process files with query
- `GET /status/{session_id}` - Get session processing status
- `GET /agents` - List available agents and capabilities
- `GET /health` - Comprehensive health check

### Document Management
- `POST /documents/add` - Add document to vector store
- `GET /documents/search` - Search documents in vector store
- `GET /stats` - Get system statistics

### Session Management
- `GET /sessions/{session_id}/history` - Get conversation history
- `POST /sessions/{session_id}/context` - Set session context

## 🛡️ Security & Privacy

- **Local Processing**: All LLM inference happens locally
- **No Data Collection**: No external API calls or data transmission
- **Privacy First**: User queries never leave your system
- **Secure by Design**: No API keys or external dependencies required

## 📊 Performance

- **Processing Time**: Typically 10-30 seconds depending on query complexity
- **Memory Usage**: ~6-8 GB RAM for full model stack
- **Concurrent Sessions**: Supports multiple simultaneous queries
- **Resource Optimization**: Efficient agent coordination and caching

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [LangGraph](https://langchain-ai.github.io/langgraph/) for agent orchestration
- [LangChain](https://python.langchain.com/) for agent framework
- [Mistral AI](https://mistral.ai/) for the open-source model
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) and [Tailwind CSS](https://tailwindcss.com/) for the frontend
- [Framer Motion](https://www.framer.com/motion/) for animations

## 🚨 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure backend is running: `cd backend && python main.py`
   - Check if port 8000 is available
   - Verify Ollama is running: `ollama serve`

2. **Ollama Connection Issues**
   - Ensure Ollama is running: `ollama serve`
   - Check if models are installed: `ollama list`
   - Verify models: `ollama pull mistral && ollama pull llava`

3. **Frontend Build Errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility (18+)

4. **Memory Issues**
   - Reduce model size: Use `phi` instead of `mistral`
   - Adjust MAX_TOKENS in .env file
   - Ensure adequate system resources (16GB+ RAM)

For more help, check the [Issues](https://github.com/yourusername/neurofluxion-ai/issues) section or create a new issue.

---

**Neurofluxion AI** - Orchestrating Intelligence — Across Voice, Vision, and Thought.