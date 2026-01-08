"""RAG (Retrieval-Augmented Generation) service using ChromaDB."""
import os
import sys
import warnings
from io import StringIO
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import uuid

from config import settings
from app.models.schemas import TrialSpecInput, ProtocolStructured

# Disable ChromaDB telemetry to suppress warning messages
os.environ['ANONYMIZED_TELEMETRY'] = 'False'


class RAGService:
    """Service for storing and retrieving protocol examples using vector database."""
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        # Initialize ChromaDB with persistent storage
        self.db_path = settings.vector_db_path
        
        # Temporarily suppress stderr to hide ChromaDB telemetry warnings
        original_stderr = sys.stderr
        sys.stderr = StringIO()
        
        try:
            # Create client with telemetry disabled
            chroma_settings = ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=chroma_settings
            )
            
            # Get or create collection for protocol examples
            self.collection = self.client.get_or_create_collection(
                name="protocol_examples",
                metadata={"description": "Clinical trial protocol examples for RAG"}
            )
        finally:
            # Restore stderr
            sys.stderr = original_stderr
        
        print(f"✓ RAG Service initialized with {self.collection.count()} protocol examples")
    
    def add_protocol_example(
        self,
        trial_spec: TrialSpecInput,
        protocol: ProtocolStructured,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a protocol example to the vector database.
        
        Args:
            trial_spec: Input trial specification
            protocol: Generated protocol
            metadata: Optional additional metadata
            
        Returns:
            Document ID in the vector database
        """
        # Create unique ID
        doc_id = f"protocol_{uuid.uuid4().hex[:12]}"
        
        # Create searchable text from trial spec
        search_text = self._create_search_text(trial_spec)
        
        # Create metadata
        doc_metadata = {
            "sponsor": trial_spec.sponsor,
            "phase": trial_spec.phase.value,
            "indication": trial_spec.indication,
            "design": trial_spec.design,
            "sample_size": trial_spec.sample_size,
            "duration_weeks": trial_spec.duration_weeks,
            "region": trial_spec.region,
            "protocol_id": protocol.protocol_id,
            "added_at": datetime.now().isoformat(),
        }
        
        if metadata:
            doc_metadata.update(metadata)
        
        # Store the complete protocol data as JSON in metadata
        doc_metadata["trial_spec_json"] = trial_spec.model_dump_json()
        
        # Convert protocol to JSON (handle datetime serialization)
        import json
        from datetime import datetime as dt_class
        
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, dt_class):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        doc_metadata["protocol_json"] = json.dumps(protocol.model_dump(), default=json_serial)
        
        # Add to vector database
        self.collection.add(
            documents=[search_text],
            metadatas=[doc_metadata],
            ids=[doc_id]
        )
        
        print(f"✓ Added protocol example: {doc_id} ({trial_spec.phase.value} - {trial_spec.indication})")
        
        return doc_id
    
    def retrieve_similar_protocols(
        self,
        trial_spec: TrialSpecInput,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar protocol examples based on trial specification.
        
        Args:
            trial_spec: Input trial specification to find similar examples
            n_results: Number of similar examples to retrieve
            
        Returns:
            List of similar protocol examples with metadata and similarity scores
        """
        # Create query text
        query_text = self._create_search_text(trial_spec)
        
        # Check if collection is empty
        if self.collection.count() == 0:
            print("⚠ No protocol examples in database")
            return []
        
        # Query vector database
        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(n_results, self.collection.count()),
        )
        
        # Format results
        similar_protocols = []
        
        if results and results['ids'] and len(results['ids'][0]) > 0:
            for i, doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i] if 'distances' in results else None
                
                # Parse stored JSON
                trial_spec_data = json.loads(metadata.pop('trial_spec_json', '{}'))
                protocol_data = json.loads(metadata.pop('protocol_json', '{}'))
                
                similar_protocols.append({
                    'id': doc_id,
                    'similarity_score': 1 - distance if distance is not None else None,
                    'distance': distance,
                    'metadata': metadata,
                    'trial_spec': trial_spec_data,
                    'protocol': protocol_data,
                })
            
            print(f"✓ Retrieved {len(similar_protocols)} similar protocol(s)")
        else:
            print("⚠ No similar protocols found")
        
        return similar_protocols
    
    def get_protocol_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific protocol by ID.
        
        Args:
            doc_id: Document ID in vector database
            
        Returns:
            Protocol data or None if not found
        """
        try:
            result = self.collection.get(ids=[doc_id])
            
            if result and result['ids']:
                metadata = result['metadatas'][0]
                
                trial_spec_data = json.loads(metadata.pop('trial_spec_json', '{}'))
                protocol_data = json.loads(metadata.pop('protocol_json', '{}'))
                
                return {
                    'id': doc_id,
                    'metadata': metadata,
                    'trial_spec': trial_spec_data,
                    'protocol': protocol_data,
                }
            
            return None
        except Exception as e:
            print(f"✗ Error retrieving protocol {doc_id}: {e}")
            return None
    
    def delete_protocol(self, doc_id: str) -> bool:
        """
        Delete a protocol example from the database.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            self.collection.delete(ids=[doc_id])
            print(f"✓ Deleted protocol: {doc_id}")
            return True
        except Exception as e:
            print(f"✗ Error deleting protocol {doc_id}: {e}")
            return False
    
    def list_all_protocols(self) -> List[Dict[str, Any]]:
        """
        List all protocol examples in the database.
        
        Returns:
            List of all protocol metadata
        """
        try:
            result = self.collection.get()
            
            protocols = []
            if result and result['ids']:
                for i, doc_id in enumerate(result['ids']):
                    metadata = result['metadatas'][i].copy()
                    # Remove large JSON fields for listing
                    metadata.pop('trial_spec_json', None)
                    metadata.pop('protocol_json', None)
                    
                    protocols.append({
                        'id': doc_id,
                        'metadata': metadata,
                    })
            
            return protocols
        except Exception as e:
            print(f"✗ Error listing protocols: {e}")
            return []
    
    def get_count(self) -> int:
        """Get the number of protocol examples in the database."""
        return self.collection.count()
    
    def clear_all(self) -> bool:
        """
        Clear all protocol examples from the database.
        Use with caution!
        
        Returns:
            True if cleared successfully
        """
        try:
            # Delete the collection and recreate it
            self.client.delete_collection("protocol_examples")
            self.collection = self.client.get_or_create_collection(
                name="protocol_examples",
                metadata={"description": "Clinical trial protocol examples for RAG"}
            )
            print("✓ Cleared all protocol examples")
            return True
        except Exception as e:
            print(f"✗ Error clearing database: {e}")
            return False
    
    def _create_search_text(self, trial_spec) -> str:
        """
        Create searchable text representation of trial specification.
        This text will be embedded and used for similarity search.
        
        Args:
            trial_spec: Trial specification (TrialSpecInput or dict)
            
        Returns:
            Searchable text string
        """
        # Handle both dict and Pydantic model
        if isinstance(trial_spec, dict):
            # Convert dict to TrialSpecInput if needed
            from app.models.schemas import TrialSpecInput
            trial_spec = TrialSpecInput(**trial_spec)
        
        # Combine key fields into searchable text
        parts = [
            f"Phase: {trial_spec.phase.value if hasattr(trial_spec.phase, 'value') else trial_spec.phase}",
            f"Indication: {trial_spec.indication}",
            f"Design: {trial_spec.design}",
            f"Sample Size: {trial_spec.sample_size}",
            f"Duration: {trial_spec.duration_weeks} weeks",
            f"Region: {trial_spec.region}",
        ]
        
        # Add endpoints
        if trial_spec.key_endpoints:
            endpoints_text = "; ".join([
                f"{ep.type.value if hasattr(ep.type, 'value') else ep.type}: {ep.name if hasattr(ep, 'name') else ep.get('name', '')}"
                for ep in trial_spec.key_endpoints
            ])
            parts.append(f"Endpoints: {endpoints_text}")
        
        # Add inclusion criteria
        if trial_spec.inclusion_criteria:
            inclusion_text = "; ".join(trial_spec.inclusion_criteria[:3])  # First 3
            parts.append(f"Inclusion: {inclusion_text}")
        
        # Add background if available
        if hasattr(trial_spec, 'background') and trial_spec.background:
            # Truncate background to 200 chars
            bg_text = trial_spec.background[:200]
            parts.append(f"Background: {bg_text}")
        
        return " | ".join(parts)
    
    def extract_relevant_context(
        self,
        similar_protocols: List[Dict[str, Any]],
        max_examples: int = 2
    ) -> str:
        """
        Extract relevant context from similar protocols for use in generation.
        
        Args:
            similar_protocols: List of similar protocol examples
            max_examples: Maximum number of examples to include in context
            
        Returns:
            Formatted context string
        """
        if not similar_protocols:
            return ""
        
        context_parts = ["Similar protocol examples found:"]
        
        for i, protocol in enumerate(similar_protocols[:max_examples], 1):
            metadata = protocol['metadata']
            score = protocol.get('similarity_score', 'N/A')
            
            context_parts.append(
                f"\n{i}. {metadata['phase']} study in {metadata['indication']}"
                f"\n   Design: {metadata['design']}"
                f"\n   Sample Size: {metadata['sample_size']}"
                f"\n   Duration: {metadata['duration_weeks']} weeks"
                f"\n   Similarity: {score:.2f if isinstance(score, float) else score}"
            )
        
        return "\n".join(context_parts)


# Global RAG service instance
_rag_service = None

def get_rag_service() -> RAGService:
    """Get or create the global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
