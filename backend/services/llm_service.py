"""
LLM service using Google Gemini
Handles chat completion, context management, and prompt engineering
"""
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime
import uuid

from models import RetrievalResult
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Manage LLM interactions with Google Gemini"""
    
    # System prompt template for RAG
    SYSTEM_PROMPT = """You are an AI assistant for Tilak Parajuli's academic website. Your role is to answer questions about Tilak's background, research, projects, experience, and skills based on the provided context.

Guidelines:
1. Answer questions accurately using ONLY the information from the provided context
2. If the answer is not in the context, politely say "I don't have that information in the available documents"
3. Be concise but comprehensive
4. Cite specific details when available (e.g., dates, project names, institutions)
5. Maintain a professional, academic tone
6. If asked about topics not related to Tilak's profile, politely redirect to relevant information

Context from documents:
{context}

User Question: {query}

Answer:"""
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    async def generate_answer(
        self,
        query: str,
        retrieved_contexts: List[RetrievalResult],
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate answer using retrieved context
        
        Args:
            query: User question
            retrieved_contexts: List of relevant document chunks
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # Prepare context from retrieved chunks
            context = self._prepare_context(retrieved_contexts)
            
            # Build prompt
            prompt = self.SYSTEM_PROMPT.format(
                context=context,
                query=query
            )
            
            # Get conversation history if available
            history = self._get_conversation_history(conversation_id)
            
            # Generate response
            if history:
                chat = self.model.start_chat(history=history)
                response = chat.send_message(prompt)
            else:
                response = self.model.generate_content(prompt)
            
            answer = response.text
            
            # Calculate confidence based on retrieval scores
            confidence = self._calculate_confidence(retrieved_contexts)
            
            # Prepare sources
            sources = self._prepare_sources(retrieved_contexts)
            
            # Generate or use conversation ID
            conv_id = conversation_id or self._generate_conversation_id()
            
            # Store in conversation history
            self._update_conversation_history(conv_id, query, answer)
            
            logger.info(f"Generated answer for query: {query[:50]}...")
            
            return {
                'answer': answer,
                'sources': sources,
                'conversation_id': conv_id,
                'confidence': confidence,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Answer generation failed: {str(e)}")
            raise
    
    def _prepare_context(self, results: List[RetrievalResult]) -> str:
        """Prepare context string from retrieval results"""
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for idx, result in enumerate(results, 1):
            source = result.metadata.get('filename', 'Unknown')
            context_parts.append(
                f"[Source {idx}: {source}]\n{result.text}\n"
            )
        
        # Truncate if too long
        context = "\n".join(context_parts)
        if len(context) > settings.MAX_CONTEXT_LENGTH:
            context = context[:settings.MAX_CONTEXT_LENGTH] + "...[truncated]"
        
        return context
    
    def _prepare_sources(self, results: List[RetrievalResult]) -> List[Dict[str, Any]]:
        """Prepare source information for response"""
        sources = []
        for result in results:
            source = {
                'text': result.text[:200] + "..." if len(result.text) > 200 else result.text,
                'score': round(result.score, 3),
                'metadata': {
                    'filename': result.metadata.get('filename', 'Unknown'),
                    'chunk_index': result.metadata.get('chunk_index', 0),
                    'document_id': result.metadata.get('document_id', '')
                }
            }
            sources.append(source)
        return sources
    
    def _calculate_confidence(self, results: List[RetrievalResult]) -> float:
        """Calculate confidence score based on retrieval quality"""
        if not results:
            return 0.0
        
        # Average of top scores
        avg_score = sum(r.score for r in results) / len(results)
        
        # Adjust based on number of results
        result_factor = min(len(results) / settings.TOP_K_RESULTS, 1.0)
        
        confidence = avg_score * result_factor
        return round(min(confidence, 1.0), 2)
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID"""
        return f"conv_{uuid.uuid4().hex[:12]}"
    
    def _get_conversation_history(
        self,
        conversation_id: Optional[str]
    ) -> List[Dict[str, str]]:
        """Retrieve conversation history"""
        if not conversation_id or conversation_id not in self.conversations:
            return []
        return self.conversations[conversation_id]
    
    def _update_conversation_history(
        self,
        conversation_id: str,
        query: str,
        answer: str
    ):
        """Update conversation history"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].extend([
            {'role': 'user', 'parts': [query]},
            {'role': 'model', 'parts': [answer]}
        ])
        
        # Keep only last 10 exchanges to manage memory
        if len(self.conversations[conversation_id]) > 20:
            self.conversations[conversation_id] = self.conversations[conversation_id][-20:]
    
    async def check_health(self) -> bool:
        """Check if LLM service is healthy"""
        try:
            response = self.model.generate_content("Hello")
            return bool(response.text)
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            return False

