"""Vector Store Implementation with ChromaDB"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
import uuid

class VectorStore:
    """In-memory vector store using ChromaDB"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        # Initialize ChromaDB in memory
        self.client = chromadb.Client(Settings(
            allow_reset=True,
            anonymized_telemetry=False
        ))
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """Add document chunks to vector store"""
        if not chunks:
            return
            
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            # Generate unique ID
            chunk_id = str(uuid.uuid4())
            
            # Extract text for embedding
            text = chunk['text']
            
            # Prepare metadata (everything except text)
            metadata = {k: v for k, v in chunk.items() if k != 'text'}
            
            documents.append(text)
            metadatas.append(metadata)
            ids.append(chunk_id)
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if self.collection.count() == 0:
            return []
        
        # Perform similarity search
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count())
        )
        
        # Format results
        formatted_results = []
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            
            result = {
                'text': doc,
                'score': results['distances'][0][i] if 'distances' in results else 0.0,
                **metadata
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        return {
            'total_documents': self.collection.count(),
            'embedding_model': self.embedding_model.get_sentence_embedding_dimension()
        }
    
    def clear(self) -> None:
        """Clear all documents from the store"""
        self.client.reset()