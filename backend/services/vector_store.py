"""
Vector store service using Pinecone
Handles embedding storage, retrieval, and similarity search
"""
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai

from models import DocumentChunk, RetrievalResult
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStoreService:
    """Manage vector embeddings in Pinecone"""
    
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.EMBED_DIMENSION
        self.index = None
        
        # Configure Google AI for embeddings
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or connect to Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )
                logger.info(f"Index {self.index_name} created successfully")
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {str(e)}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text using Google's embedding model
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        try:
            result = genai.embed_content(
                model=f"models/{settings.EMBED_MODEL}",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for search query
        
        Args:
            query: Search query text
            
        Returns:
            List of embedding values
        """
        try:
            result = genai.embed_content(
                model=f"models/{settings.EMBED_MODEL}",
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Query embedding failed: {str(e)}")
            raise
    
    async def upsert_chunks(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Store document chunks with embeddings in Pinecone
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            Upsert statistics
        """
        try:
            vectors = []
            
            for chunk in chunks:
                # Generate embedding if not present
                if not chunk.embedding:
                    chunk.embedding = await self.embed_text(chunk.text)
                
                # Prepare vector for Pinecone
                vector = {
                    'id': chunk.chunk_id,
                    'values': chunk.embedding,
                    'metadata': {
                        'text': chunk.text[:1000],  # Store truncated text in metadata
                        'document_id': chunk.document_id,
                        'chunk_index': chunk.chunk_index,
                        **chunk.metadata
                    }
                }
                vectors.append(vector)
            
            # Batch upsert to Pinecone
            upsert_response = self.index.upsert(vectors=vectors)
            
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
            return {
                'upserted_count': upsert_response.upserted_count,
                'chunks': len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Failed to upsert chunks: {str(e)}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """
        Search for similar chunks using vector similarity
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of RetrievalResult objects
        """
        try:
            top_k = top_k or settings.TOP_K_RESULTS
            
            # Generate query embedding
            query_embedding = await self.embed_query(query)
            
            # Search Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Convert to RetrievalResult objects
            results = []
            for match in search_results.matches:
                if match.score >= settings.SIMILARITY_THRESHOLD:
                    result = RetrievalResult(
                        text=match.metadata.get('text', ''),
                        score=match.score,
                        metadata=match.metadata
                    )
                    results.append(result)
            
            logger.info(f"Found {len(results)} relevant chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete all chunks for a document
        
        Args:
            document_id: Document identifier
            
        Returns:
            Deletion statistics
        """
        try:
            # Delete by metadata filter
            delete_response = self.index.delete(
                filter={'document_id': document_id}
            )
            
            logger.info(f"Deleted chunks for document: {document_id}")
            return {'document_id': document_id, 'status': 'deleted'}
            
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {}

