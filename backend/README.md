# Academic RAG Backend API

Production-ready RAG (Retrieval-Augmented Generation) backend for academic personal website with document upload and intelligent Q&A capabilities.

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│ LLM  │  │Vector │
│Gemini│  │ Store │
└──────┘  │Pinecone
          └────────┘
```

### Components

- **FastAPI**: Modern async web framework
- **Google Gemini**: LLM for answer generation
- **Pinecone**: Vector database for semantic search
- **Document Processor**: PDF/TXT/MD/DOCX support with intelligent chunking

## 🚀 Features

- ✅ Document upload (PDF, TXT, MD, DOCX)
- ✅ Intelligent text chunking with overlap
- ✅ Semantic search with vector embeddings
- ✅ Context-aware answer generation
- ✅ Conversation history tracking
- ✅ CORS support for web integration
- ✅ Comprehensive error handling
- ✅ Health monitoring
- ✅ Production-ready logging

## 📋 Prerequisites

- Python 3.11+
- Google AI API key ([Get here](https://ai.google.dev/))
- Pinecone API key ([Get here](https://www.pinecone.io/))

## 🛠️ Installation

### Local Development

1. **Clone and navigate to backend**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp env.example .env
# Edit .env with your API keys
```

5. **Run the server**:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

### Docker Deployment

1. **Build and run**:
```bash
docker-compose up --build
```

2. **Access API**:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

## 📡 API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "vector_store": "healthy",
    "llm": "healthy"
  }
}
```

### Upload Document
```http
POST /upload
Content-Type: multipart/form-data

file: <your_file.pdf>
```

Response:
```json
{
  "document_id": "abc123",
  "filename": "cv.pdf",
  "status": "completed",
  "chunks_created": 15,
  "message": "Document processed successfully"
}
```

### Chat (RAG Query)
```http
POST /chat
Content-Type: application/json

{
  "query": "What is Tilak's research focus?",
  "conversation_id": "conv_123" // optional
}
```

Response:
```json
{
  "answer": "Tilak's research focuses on...",
  "sources": [
    {
      "text": "Relevant context...",
      "score": 0.89,
      "metadata": {"filename": "cv.pdf"}
    }
  ],
  "conversation_id": "conv_123",
  "confidence": 0.85
}
```

### List Documents
```http
GET /documents
```

### Delete Document
```http
DELETE /documents/{document_id}
```

## 🌐 Vercel Deployment

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Set environment variables** in Vercel dashboard:
   - `GOOGLE_API_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_INDEX_NAME`

3. **Deploy**:
```bash
vercel --prod
```

## 🔧 Configuration

Edit `config.py` or set environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key | Required |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `LLM_MODEL` | Gemini model | `gemini-1.5-flash` |
| `EMBED_MODEL` | Embedding model | `text-embedding-004` |
| `CHUNK_SIZE` | Text chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `TOP_K_RESULTS` | Retrieval results | `5` |
| `SIMILARITY_THRESHOLD` | Min similarity | `0.7` |

## 📁 Project Structure

```
backend/
├── app.py                 # FastAPI application
├── config.py              # Configuration management
├── models.py              # Pydantic models
├── services/
│   ├── document_processor.py  # Document parsing & chunking
│   ├── vector_store.py        # Pinecone integration
│   └── llm_service.py         # Gemini LLM service
├── utils/
│   └── logger.py          # Logging configuration
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose
├── vercel.json            # Vercel deployment
└── README.md              # This file
```

## 🧪 Testing

### Manual Testing

1. **Upload a document**:
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/document.pdf"
```

2. **Query the system**:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main projects?"}'
```

### API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔒 Security Considerations

- ✅ CORS configured for specific origins
- ✅ File size limits enforced
- ✅ Input validation with Pydantic
- ✅ Error messages sanitized in production
- ✅ Non-root Docker user
- ⚠️ Add rate limiting for production (e.g., slowapi)
- ⚠️ Implement authentication for upload endpoint
- ⚠️ Use secrets manager for API keys

## 📊 Monitoring

- Health endpoint: `/health`
- Structured logging with timestamps
- Service status checks for all components

## 🐛 Troubleshooting

### Common Issues

1. **"Service unavailable" errors**:
   - Check API keys are set correctly
   - Verify Pinecone index exists
   - Check network connectivity

2. **Embedding dimension mismatch**:
   - Ensure `EMBED_DIMENSION` matches your model
   - `text-embedding-004` uses 768 dimensions

3. **File upload fails**:
   - Check file size < `MAX_FILE_SIZE_MB`
   - Verify file extension is supported
   - Ensure sufficient memory

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, Google Gemini, and Pinecone
