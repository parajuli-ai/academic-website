"""
Document processing service
Handles PDF, TXT, MD, DOCX parsing and intelligent chunking
"""
import io
import re
from typing import List, Dict, Any
from pathlib import Path
import hashlib

# Document parsing libraries
from pypdf import PdfReader
import docx

from models import DocumentChunk, DocumentType
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Process and chunk documents for RAG"""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    async def process_file(
        self,
        file_content: bytes,
        filename: str,
        document_id: str,
        metadata: Dict[str, Any] = None
    ) -> List[DocumentChunk]:
        """
        Process uploaded file and create chunks
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            document_id: Unique document identifier
            metadata: Additional metadata
            
        Returns:
            List of DocumentChunk objects
        """
        try:
            # Detect document type
            doc_type = self._get_document_type(filename)
            
            # Extract text based on type
            text = await self._extract_text(file_content, doc_type)
            
            if not text or len(text.strip()) < 10:
                raise ValueError(f"Insufficient text extracted from {filename}")
            
            # Create chunks with intelligent splitting
            chunks = self._create_chunks(text, document_id, filename, metadata or {})
            
            logger.info(f"Processed {filename}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            raise
    
    async def _extract_text(self, content: bytes, doc_type: DocumentType) -> str:
        """Extract text from different document types"""
        try:
            if doc_type == DocumentType.PDF:
                return self._extract_from_pdf(content)
            elif doc_type == DocumentType.DOCX:
                return self._extract_from_docx(content)
            elif doc_type in [DocumentType.TXT, DocumentType.MD]:
                return content.decode('utf-8', errors='ignore')
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise
    
    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    # Add page marker for metadata
                    text_parts.append(f"[Page {page_num}]\n{page_text}")
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
    
    def _create_chunks(
        self,
        text: str,
        document_id: str,
        filename: str,
        metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Create intelligent chunks with semantic boundaries
        Uses sentence-aware splitting to maintain context
        """
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Split into sentences for intelligent chunking
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check if adding this sentence exceeds chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create chunk from accumulated sentences
                chunk_text = " ".join(current_chunk)
                chunk = self._create_chunk(
                    chunk_text, document_id, filename, chunk_index, metadata
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk, self.chunk_overlap
                )
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk)
                chunk_index += 1
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk = self._create_chunk(
                chunk_text, document_id, filename, chunk_index, metadata
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(
        self,
        text: str,
        document_id: str,
        filename: str,
        chunk_index: int,
        metadata: Dict[str, Any]
    ) -> DocumentChunk:
        """Create a DocumentChunk object"""
        chunk_id = self._generate_chunk_id(document_id, chunk_index)
        
        chunk_metadata = {
            "filename": filename,
            "chunk_index": chunk_index,
            "document_id": document_id,
            **metadata
        }
        
        return DocumentChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            text=text,
            metadata=chunk_metadata,
            chunk_index=chunk_index
        )
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might cause issues
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text.strip()
    
    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """Split text into sentences using regex"""
        # Split on sentence boundaries
        sentence_endings = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def _get_overlap_sentences(sentences: List[str], overlap_chars: int) -> List[str]:
        """Get sentences for overlap based on character count"""
        overlap_sentences = []
        char_count = 0
        
        for sentence in reversed(sentences):
            if char_count >= overlap_chars:
                break
            overlap_sentences.insert(0, sentence)
            char_count += len(sentence)
        
        return overlap_sentences
    
    @staticmethod
    def _get_document_type(filename: str) -> DocumentType:
        """Determine document type from filename"""
        ext = Path(filename).suffix.lower()
        
        type_map = {
            '.pdf': DocumentType.PDF,
            '.txt': DocumentType.TXT,
            '.md': DocumentType.MD,
            '.docx': DocumentType.DOCX,
        }
        
        if ext not in type_map:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return type_map[ext]
    
    @staticmethod
    def _generate_chunk_id(document_id: str, chunk_index: int) -> str:
        """Generate unique chunk ID"""
        content = f"{document_id}_{chunk_index}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

