"""Main FastAPI application."""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any
import uuid
from datetime import datetime
import os
import json
import logging

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from config import settings
from app.models.schemas import (
    TrialSpecInput,
    GenerationResult,
    ExportRequest,
    ValidationResult,
    ExportFormat,
)
from app.services.generator import ProtocolTemplateGenerator, CRFGenerator
from app.services.validator import ClinicalRulesValidator
from app.services.exporter import ProtocolExporter
from app.services.rag_service import get_rag_service


# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="AI-Generated Clinical Trial Protocol and EDC Configuration API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
# Note: use_llm=True enables OpenAI GPT-4 integration for enhanced protocol generation
# Requires OPENAI_API_KEY in .env file. Falls back gracefully to RAG-only if unavailable.
protocol_generator = ProtocolTemplateGenerator(use_rag=True, use_llm=True)
crf_generator = CRFGenerator()
validator = ClinicalRulesValidator()
exporter = ProtocolExporter()
rag_service = get_rag_service()

# In-memory storage for generated protocols (use database in production)
generated_protocols: Dict[str, GenerationResult] = {}

# Mount static files for web UI
web_dir = os.path.join(os.path.dirname(__file__), "web")
if os.path.exists(web_dir):
    app.mount("/ui", StaticFiles(directory=web_dir, html=True), name="ui")


@app.get("/")
async def root():
    """Root endpoint - redirect to web UI or API information."""
    return FileResponse(os.path.join(web_dir, "index.html")) if os.path.exists(web_dir) else {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "operational",
        "web_ui": "/ui",
        "endpoints": {
            "docs": "/docs",
            "generate": "/api/v1/generate",
            "validate": "/api/v1/validate",
            "export": "/api/v1/export",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/v1/generate", response_model=GenerationResult, status_code=status.HTTP_201_CREATED)
async def generate_protocol(trial_spec: TrialSpecInput):
    """
    Generate a complete clinical trial protocol and CRF schema.
    
    This endpoint accepts a trial specification and produces:
    - Structured protocol JSON
    - Human-readable protocol text
    - CRF schema with forms, fields, and visit schedule
    - Validation results
    
    Args:
        trial_spec: Trial specification input
        
    Returns:
        GenerationResult: Complete generated protocol and CRF artifacts
    """
    try:
        print("\n" + "="*80)
        print(f"🚀 ENDPOINT HIT: /api/v1/generate")
        print(f"📋 Title: {trial_spec.title}")
        print(f"💊 Indication: {trial_spec.indication}")
        print(f"📝 Additional Instructions: {trial_spec.additional_instructions[:100] if trial_spec.additional_instructions else 'None'}")
        print("="*80 + "\n")
        
        logger.info(f"Generating protocol for: {trial_spec.title}")
        logger.debug(f"Trial spec: phase={trial_spec.phase.value}, indication={trial_spec.indication}")
        
        # Generate unique request ID
        request_id = f"REQ-{uuid.uuid4().hex[:12].upper()}"
        logger.debug(f"Generated request_id: {request_id}")
        
        # Validate input specification
        validation_result = validator.validate_trial_spec(trial_spec)
        
        if not validation_result.valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Trial specification validation failed",
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings,
                }
            )
        
        # Generate structured protocol
        protocol_structured = protocol_generator.generate_structured_protocol(trial_spec)
        
        # Generate narrative protocol text
        protocol_text = protocol_generator.generate_protocol_narrative(trial_spec)
        
        # Generate CRF schema
        crf_schema = crf_generator.generate_crf_schema(trial_spec, protocol_structured)
        
        # Validate generated protocol
        protocol_validation = validator.validate_protocol(protocol_structured)
        
        # Validate CRF schema
        crf_validation = validator.validate_crf_schema(crf_schema)
        
        # Combine validation messages
        all_warnings = (
            validation_result.warnings +
            protocol_validation.warnings +
            crf_validation.warnings
        )
        
        all_errors = protocol_validation.errors + crf_validation.errors
        
        # Determine validation status
        if all_errors:
            validation_status = "failed"
        elif all_warnings:
            validation_status = "warnings"
        else:
            validation_status = "passed"
        
        # Calculate overall confidence based on multiple factors
        confidence_factors = []
        
        # Factor 1: RAG similarity (if available)
        if protocol_structured.rag_avg_similarity is not None:
            # RAG similarity is 0-1, higher is better
            # Good similarity (>0.7) = high confidence, poor (<0.5) = lower confidence
            rag_confidence = min(1.0, protocol_structured.rag_avg_similarity + 0.2)
            confidence_factors.append(rag_confidence)
        
        # Factor 2: LLM enhancement coverage (if LLM was used)
        if protocol_structured.llm_enhanced_sections:
            # More sections enhanced = higher confidence
            # Expect up to 7 sections (objectives, criteria, design, endpoints, visits, assessments, CRF)
            llm_coverage = min(1.0, len(protocol_structured.llm_enhanced_sections) / 7.0)
            # LLM enhancement gets high base confidence (0.85) + bonus for coverage
            llm_confidence = 0.85 + (llm_coverage * 0.15)
            confidence_factors.append(llm_confidence)
        
        # Factor 3: Section-level confidence scores
        section_confidences = [
            s.confidence_score for s in protocol_structured.sections
            if s.confidence_score is not None
        ]
        if section_confidences:
            section_avg = sum(section_confidences) / len(section_confidences)
            confidence_factors.append(section_avg)
        
        # Factor 4: Validation status impact
        if validation_status == "passed":
            confidence_factors.append(1.0)
        elif validation_status == "warnings":
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.7)
        
        # Calculate weighted average (give more weight to RAG and LLM if available)
        if confidence_factors:
            # If we have RAG and LLM, they dominate the confidence
            if protocol_structured.rag_avg_similarity is not None and protocol_structured.llm_enhanced_sections:
                weights = [0.4, 0.4, 0.1, 0.1][:len(confidence_factors)]  # RAG=40%, LLM=40%, Sections=10%, Validation=10%
            elif protocol_structured.llm_enhanced_sections:
                weights = [0.6, 0.2, 0.2][:len(confidence_factors)]  # LLM=60%, Sections=20%, Validation=20%
            else:
                weights = [1.0/len(confidence_factors)] * len(confidence_factors)  # Equal weights
            
            overall_confidence = sum(f * w for f, w in zip(confidence_factors, weights))
            overall_confidence = min(1.0, max(0.0, overall_confidence))  # Clamp to 0-1
        else:
            overall_confidence = 0.75  # Default fallback
        
        # Create generation result
        result = GenerationResult(
            request_id=request_id,
            generated_at=datetime.now(),
            input_spec=trial_spec,
            protocol_structured=protocol_structured,
            protocol_text=protocol_text,
            crf_schema=crf_schema,
            overall_confidence=overall_confidence,
            validation_status=validation_status,
            validation_messages=all_warnings + all_errors,
            generation_method=protocol_structured.generation_method or "template_based",
            templates_used=["standard_protocol_v1", "cdash_crf_v1"],
            rag_protocols_used=protocol_structured.rag_protocols_used,
            llm_sections=protocol_structured.llm_enhanced_sections,
        )
        
        # Store result
        generated_protocols[request_id] = result
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Protocol generation failed: {str(e)}"
        )


@app.post("/api/v1/validate")
async def validate_trial_spec(trial_spec: TrialSpecInput) -> ValidationResult:
    """
    Validate a trial specification without generating protocol.
    
    Args:
        trial_spec: Trial specification to validate
        
    Returns:
        ValidationResult: Validation results with errors and warnings
    """
    try:
        validation_result = validator.validate_trial_spec(trial_spec)
        return validation_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@app.post("/api/v1/export")
async def export_protocol(export_request: ExportRequest):
    """
    Export a generated protocol in the specified format.
    
    Supported formats:
    - ODM XML (CDISC ODM)
    - FHIR JSON
    - CSV (data dictionary)
    - JSON (complete export)
    
    Args:
        export_request: Export request with format specification
        
    Returns:
        Export file content and metadata
    """
    try:
        # Retrieve generated protocol
        if export_request.request_id not in generated_protocols:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with request_id {export_request.request_id} not found"
            )
        
        result = generated_protocols[export_request.request_id]
        
        # Export to requested format
        export_data = exporter.export(
            protocol=result.protocol_structured,
            crf_schema=result.crf_schema,
            format=export_request.format,
            include_protocol=export_request.include_protocol,
            include_crf=export_request.include_crf,
        )
        
        return {
            "request_id": export_request.request_id,
            "format": export_data["format"],
            "filename": export_data["filename"],
            "content": export_data["content"],
            "generated_at": datetime.now().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@app.post("/api/v1/export/odm")
async def export_odm(request_data: Dict[str, str]):
    """
    Export protocol to CDISC ODM XML format.
    
    Args:
        request_data: Dict with request_id
        
    Returns:
        ODM XML export
    """
    try:
        request_id = request_data.get("request_id")
        if not request_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="request_id is required"
            )
        
        if request_id not in generated_protocols:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with request_id {request_id} not found"
            )
        
        result = generated_protocols[request_id]
        
        # Export to ODM XML
        export_data = exporter.export(
            protocol=result.protocol_structured,
            crf_schema=result.crf_schema,
            format=ExportFormat.ODM_XML,
            include_protocol=True,
            include_crf=True,
        )
        
        return {
            "request_id": request_id,
            "format": "ODM_XML",
            "odm_xml": export_data["content"],
            "filename": export_data["filename"],
            "generated_at": datetime.now().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ODM export failed: {str(e)}"
        )


@app.post("/api/v1/export/fhir")
async def export_fhir(request_data: Dict[str, str]):
    """
    Export protocol to FHIR JSON format.
    
    Args:
        request_data: Dict with request_id
        
    Returns:
        FHIR JSON export
    """
    try:
        request_id = request_data.get("request_id")
        if not request_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="request_id is required"
            )
        
        if request_id not in generated_protocols:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with request_id {request_id} not found"
            )
        
        result = generated_protocols[request_id]
        
        # Export to FHIR JSON
        export_data = exporter.export(
            protocol=result.protocol_structured,
            crf_schema=result.crf_schema,
            format=ExportFormat.FHIR_JSON,
            include_protocol=True,
            include_crf=True,
        )
        
        # Parse the JSON string if it's a string
        fhir_content = export_data["content"]
        if isinstance(fhir_content, str):
            fhir_content = json.loads(fhir_content)
        
        return {
            "request_id": request_id,
            "format": "FHIR_JSON",
            "fhir_bundle": fhir_content,
            "filename": export_data["filename"],
            "generated_at": datetime.now().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FHIR export failed: {str(e)}"
        )


@app.post("/api/v1/export/csv")
async def export_csv(request_data: Dict[str, str]):
    """
    Export protocol to CSV format.
    
    Args:
        request_data: Dict with request_id
        
    Returns:
        CSV export
    """
    try:
        request_id = request_data.get("request_id")
        if not request_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="request_id is required"
            )
        
        if request_id not in generated_protocols:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with request_id {request_id} not found"
            )
        
        result = generated_protocols[request_id]
        
        # Export to CSV
        export_data = exporter.export(
            protocol=result.protocol_structured,
            crf_schema=result.crf_schema,
            format=ExportFormat.CSV,
            include_protocol=True,
            include_crf=True,
        )
        
        return {
            "request_id": request_id,
            "format": "CSV",
            "csv_content": export_data["content"],
            "filename": export_data["filename"],
            "generated_at": datetime.now().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSV export failed: {str(e)}"
        )


@app.get("/api/v1/protocols/{request_id}")
async def get_protocol(request_id: str) -> GenerationResult:
    """
    Retrieve a previously generated protocol by request ID.
    
    Args:
        request_id: Unique request identifier
        
    Returns:
        GenerationResult: Complete generated protocol
    """
    if request_id not in generated_protocols:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protocol with request_id {request_id} not found"
        )
    
    return generated_protocols[request_id]


@app.get("/api/v1/protocols")
async def list_protocols():
    """
    List all generated protocols.
    
    Returns:
        List of protocol summaries
    """
    summaries = []
    for request_id, result in generated_protocols.items():
        summaries.append({
            "request_id": request_id,
            "protocol_id": result.protocol_structured.protocol_id,
            "title": result.protocol_structured.title,
            "phase": result.protocol_structured.phase,
            "generated_at": result.generated_at.isoformat(),
            "validation_status": result.validation_status,
        })
    
    return {
        "count": len(summaries),
        "protocols": summaries,
    }


@app.delete("/api/v1/protocols/{request_id}")
async def delete_protocol(request_id: str):
    """
    Delete a generated protocol.
    
    Args:
        request_id: Unique request identifier
        
    Returns:
        Deletion confirmation
    """
    if request_id not in generated_protocols:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protocol with request_id {request_id} not found"
        )
    
    del generated_protocols[request_id]
    
    return {
        "message": "Protocol deleted successfully",
        "request_id": request_id,
    }


# ===== RAG Endpoints =====

@app.post("/api/v1/rag/add-example")
async def add_protocol_example(request_id: str):
    """
    Add a generated protocol to the RAG vector database as an example.
    
    This allows the system to learn from generated protocols and use them
    to improve future generations through retrieval-augmented generation.
    
    Args:
        request_id: Request ID of a previously generated protocol
        
    Returns:
        Confirmation with vector DB document ID
    """
    try:
        # Get the generated protocol
        if request_id not in generated_protocols:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with request_id {request_id} not found"
            )
        
        result = generated_protocols[request_id]
        
        # Add to vector database
        doc_id = rag_service.add_protocol_example(
            trial_spec=result.input_spec,
            protocol=result.protocol_structured,
            metadata={
                "request_id": request_id,
                "validation_status": result.validation_status,
                "overall_confidence": result.overall_confidence,
            }
        )
        
        return {
            "message": "Protocol added to RAG database",
            "request_id": request_id,
            "rag_doc_id": doc_id,
            "total_examples": rag_service.get_count(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add protocol to RAG database: {str(e)}"
        )


@app.post("/api/v1/rag/search")
async def search_similar_protocols(trial_spec: TrialSpecInput, n_results: int = 3):
    """
    Search for similar protocols in the RAG database.
    
    This endpoint allows you to find similar protocol examples based on
    a trial specification, useful for understanding what similar studies exist.
    
    Args:
        trial_spec: Trial specification to search for
        n_results: Number of similar protocols to return (default: 3)
        
    Returns:
        List of similar protocols with similarity scores
    """
    try:
        similar_protocols = rag_service.retrieve_similar_protocols(
            trial_spec=trial_spec,
            n_results=n_results
        )
        
        # Format response
        results = []
        for protocol in similar_protocols:
            results.append({
                "rag_doc_id": protocol['id'],
                "similarity_score": protocol.get('similarity_score'),
                "metadata": protocol['metadata'],
                "trial_spec_summary": {
                    "phase": protocol['trial_spec'].get('phase'),
                    "indication": protocol['trial_spec'].get('indication'),
                    "sample_size": protocol['trial_spec'].get('sample_size'),
                    "duration_weeks": protocol['trial_spec'].get('duration_weeks'),
                }
            })
        
        return {
            "query_summary": {
                "phase": trial_spec.phase.value,
                "indication": trial_spec.indication,
            },
            "found": len(results),
            "similar_protocols": results,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@app.get("/api/v1/rag/examples")
async def list_rag_examples():
    """
    List all protocol examples in the RAG database.
    
    Returns:
        List of all protocol examples with metadata
    """
    try:
        protocols = rag_service.list_all_protocols()
        
        return {
            "total_count": len(protocols),
            "examples": protocols,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list examples: {str(e)}"
        )


@app.get("/api/v1/rag/examples/{doc_id}")
async def get_rag_example(doc_id: str):
    """
    Get a specific protocol example from the RAG database.
    
    Args:
        doc_id: RAG document ID
        
    Returns:
        Complete protocol example data
    """
    try:
        protocol = rag_service.get_protocol_by_id(doc_id)
        
        if not protocol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol example {doc_id} not found in RAG database"
            )
        
        return protocol
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve example: {str(e)}"
        )


@app.delete("/api/v1/rag/examples/{doc_id}")
async def delete_rag_example(doc_id: str):
    """
    Delete a protocol example from the RAG database.
    
    Args:
        doc_id: RAG document ID to delete
        
    Returns:
        Deletion confirmation
    """
    try:
        success = rag_service.delete_protocol(doc_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol example {doc_id} not found"
            )
        
        return {
            "message": "Protocol example deleted from RAG database",
            "doc_id": doc_id,
            "remaining_count": rag_service.get_count(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete example: {str(e)}"
        )


@app.post("/api/v1/rag/seed")
async def seed_rag_database():
    """
    Seed the RAG database with sample protocols.
    
    This endpoint populates the vector database with predefined sample protocols
    covering various therapeutic areas and phases. Useful for initial setup and testing.
    
    Returns:
        Summary of seeded protocols
    """
    try:
        from app.services.sample_protocols import SAMPLE_PROTOCOLS
        
        added_count = 0
        failed_count = 0
        doc_ids = []
        
        for sample_spec in SAMPLE_PROTOCOLS:
            try:
                # Generate protocol for the sample
                protocol = protocol_generator.generate_structured_protocol(sample_spec)
                
                # Add to RAG database
                doc_id = rag_service.add_protocol_example(
                    trial_spec=sample_spec,
                    protocol=protocol,
                    metadata={"source": "sample_seed"}
                )
                
                doc_ids.append({
                    "doc_id": doc_id,
                    "phase": sample_spec.phase.value,
                    "indication": sample_spec.indication,
                })
                added_count += 1
                
            except Exception as e:
                print(f"Failed to add sample protocol: {e}")
                failed_count += 1
        
        return {
            "message": "RAG database seeded with sample protocols",
            "added": added_count,
            "failed": failed_count,
            "total_examples": rag_service.get_count(),
            "seeded_protocols": doc_ids,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seeding failed: {str(e)}"
        )


@app.get("/api/v1/rag/stats")
async def get_rag_stats():
    """
    Get statistics about the RAG database.
    
    Returns:
        RAG database statistics
    """
    try:
        protocols = rag_service.list_all_protocols()
        
        # Aggregate statistics
        phases = {}
        indications = {}
        
        for protocol in protocols:
            metadata = protocol.get('metadata', {})
            
            phase = metadata.get('phase', 'Unknown')
            phases[phase] = phases.get(phase, 0) + 1
            
            indication = metadata.get('indication', 'Unknown')
            indications[indication] = indications.get(indication, 0) + 1
        
        return {
            "total_examples": len(protocols),
            "by_phase": phases,
            "by_indication": indications,
            "database_path": settings.vector_db_path,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True if settings.api_environment == "development" else False,
    )
