"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types"""
    PDF = "pdf"
    TXT = "txt"
    MD = "md"
    DOCX = "docx"


class DocumentStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================
# Request Models
# ============================================

class ChatRequest(BaseModel):
    """Chat request with user query"""
    query: str = Field(..., min_length=1, max_length=1000, description="User question")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents"""
    filename: str
    document_type: DocumentType
    source: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = []
    custom_metadata: Dict[str, Any] = {}


# ============================================
# Response Models
# ============================================

class ChatResponse(BaseModel):
    """Chat response with answer and sources"""
    answer: str
    sources: List[Dict[str, Any]]
    conversation_id: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Tilak Parajuli is an AI/ML researcher...",
                "sources": [
                    {
                        "text": "Relevant context chunk...",
                        "metadata": {"source": "cv.pdf", "page": 1}
                    }
                ],
                "conversation_id": "conv_123",
                "confidence": 0.85,
                "timestamp": "2024-10-18T10:30:00"
            }
        }


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: str
    filename: str
    status: DocumentStatus
    chunks_created: int
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentInfo(BaseModel):
    """Information about a stored document"""
    document_id: str
    filename: str
    document_type: DocumentType
    upload_date: datetime
    chunk_count: int
    status: DocumentStatus
    metadata: Dict[str, Any] = {}


class DocumentListResponse(BaseModel):
    """List of documents in the system"""
    documents: List[DocumentInfo]
    total_count: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    services: Dict[str, str] = {}


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================
# Internal Models
# ============================================

class DocumentChunk(BaseModel):
    """Internal model for document chunks"""
    chunk_id: str
    document_id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any]
    chunk_index: int


class RetrievalResult(BaseModel):
    """Result from vector search"""
    text: str
    score: float
    metadata: Dict[str, Any]

