"""
FastAPI RAG Backend Application
Production-ready API for academic website chat system
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional
import hashlib
from datetime import datetime
import uuid
import os

from config import settings
from models import (
    ChatRequest, ChatResponse, DocumentUploadResponse,
    DocumentListResponse, HealthResponse, ErrorResponse,
    DocumentStatus, DocumentInfo, DocumentType
)
from services import DocumentProcessor, VectorStoreService, LLMService
from utils.logger import get_logger

logger = get_logger(__name__)

# ============================================
# Service Instances (Singleton Pattern)
# ============================================
doc_processor: Optional[DocumentProcessor] = None
vector_store: Optional[VectorStoreService] = None
llm_service: Optional[LLMService] = None

# Document tracking (in-memory for now, use DB in production)
documents_db: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global doc_processor, vector_store, llm_service
    
    logger.info("Starting RAG backend services...")
    
    try:
        # Initialize services
        doc_processor = DocumentProcessor()
        vector_store = VectorStoreService()
        llm_service = LLMService()
        
        logger.info("All services initialized successfully")
        yield
        
    except Exception as e:
        logger.warning(f"Failed to initialize services: {str(e)}")
        logger.warning("Server will start in limited mode - some endpoints may not work")
        yield
    finally:
        logger.info("Shutting down RAG backend services...")

# ============================================
# FastAPI Application
# ============================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG-powered chat API for academic personal website",
    lifespan=lifespan
)

# ============================================
# Middleware
# ============================================
# Parse ALLOWED_ORIGINS from environment variable
# allowed_origins = os.getenv("ALLOWED_ORIGINS", '["http://localhost:4000", "https://parajuli-ai.github.io"]').strip('[]').split(',')

allowed_origins = json.loads(os.getenv(
    "ALLOWED_ORIGINS",
    '["http://localhost:4000", "https://parajuli-ai.github.io"]'
))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Dependency Injection
# ============================================
def get_doc_processor() -> DocumentProcessor:
    if doc_processor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document processor not initialized"
        )
    return doc_processor

def get_vector_store() -> VectorStoreService:
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    return vector_store

def get_llm_service() -> LLMService:
    if llm_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not initialized"
        )
    return llm_service

# ============================================
# API Routes
# ============================================

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Academic RAG API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check(
    vs: VectorStoreService = Depends(get_vector_store),
    llm: LLMService = Depends(get_llm_service)
):
    """
    Health check endpoint
    Verifies all services are operational
    """
    try:
        # Check vector store
        vs_stats = await vs.get_index_stats()
        vs_status = "healthy" if vs_stats else "degraded"
        
        # Check LLM
        llm_status = "healthy" if await llm.check_health() else "degraded"
        
        overall_status = "healthy" if vs_status == "healthy" and llm_status == "healthy" else "degraded"
        
        return HealthResponse(
            status=overall_status,
            version=settings.APP_VERSION,
            services={
                "vector_store": vs_status,
                "llm": llm_status,
                "document_processor": "healthy"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version=settings.APP_VERSION,
            services={"error": str(e)}
        )

@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    dp: DocumentProcessor = Depends(get_doc_processor),
    vs: VectorStoreService = Depends(get_vector_store)
):
    """
    Upload and process a document
    Supports: PDF, TXT, MD, DOCX
    """
    try:
        # Validate file size
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
            )
        
        # Validate file extension
        file_ext = file.filename.split('.')[-1].lower()
        if f".{file_ext}" not in settings.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Supported: {', '.join(settings.SUPPORTED_EXTENSIONS)}"
            )
        
        # Generate document ID
        document_id = hashlib.sha256(
            f"{file.filename}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        logger.info(f"Processing upload: {file.filename} (ID: {document_id})")
        
        # Process document
        chunks = await dp.process_file(
            file_content=content,
            filename=file.filename,
            document_id=document_id,
            metadata={"upload_date": datetime.utcnow().isoformat()}
        )
        
        # Store in vector database
        await vs.upsert_chunks(chunks)
        
        # Track document
        documents_db[document_id] = DocumentInfo(
            document_id=document_id,
            filename=file.filename,
            document_type=DocumentType(file_ext),
            upload_date=datetime.utcnow(),
            chunk_count=len(chunks),
            status=DocumentStatus.COMPLETED,
            metadata={"file_size_mb": round(file_size_mb, 2)}
        )
        
        logger.info(f"Successfully processed {file.filename}: {len(chunks)} chunks")
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            status=DocumentStatus.COMPLETED,
            chunks_created=len(chunks),
            message=f"Document processed successfully with {len(chunks)} chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed for {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    vs: VectorStoreService = Depends(get_vector_store),
    llm: LLMService = Depends(get_llm_service)
):
    """
    Chat endpoint with RAG
    Retrieves relevant context and generates answer
    """
    try:
        logger.info(f"Chat request: {request.query[:50]}...")
        
        # Retrieve relevant chunks
        retrieved_contexts = await vs.search(
            query=request.query,
            top_k=settings.TOP_K_RESULTS
        )
        
        if not retrieved_contexts:
            return ChatResponse(
                answer="I don't have any information about that in the available documents. Please ask about Tilak Parajuli's background, research, projects, or experience.",
                sources=[],
                conversation_id=request.conversation_id or f"conv_{uuid.uuid4().hex[:12]}",
                confidence=0.0
            )
        
        # Generate answer using LLM
        result = await llm.generate_answer(
            query=request.query,
            retrieved_contexts=retrieved_contexts,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )

@app.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    List all uploaded documents
    """
    try:
        docs = list(documents_db.values())
        return DocumentListResponse(
            documents=docs,
            total_count=len(docs)
        )
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    vs: VectorStoreService = Depends(get_vector_store)
):
    """
    Delete a document and its chunks
    """
    try:
        if document_id not in documents_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Delete from vector store
        await vs.delete_document(document_id)
        
        # Remove from tracking
        del documents_db[document_id]
        
        logger.info(f"Deleted document: {document_id}")
        
        return {"message": f"Document {document_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================
# Error Handlers
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=str(exc)
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.DEBUG else None
        ).model_dump()
    )
