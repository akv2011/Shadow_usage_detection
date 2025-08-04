#!/usr/bin/env python3
"""
Backend API for Shadow AI Detection Tool

This module provides a FastAPI-based web server that exposes the detection
engine functionality via REST API endpoints. The API supports both text input
and file upload for code analysis.

Endpoints:
    POST /api/check - Analyze raw code text
    POST /api/analyze - Analyze uploaded file
    GET /api/health - Health check endpoint
    GET /docs - Automatic API documentation

Author: Shadow AI Detection Tool
Created: 2025-08-04
"""

import io
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
import uvicorn

# Import our modules
from shadow_ai.engine import analyze
from shadow_ai.parser import parse, ParserError, InvalidInputError, FileTooLargeError
from shadow_ai.database import init_database, get_database


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Shadow AI Detection API",
    description="Heuristic-based tool for detecting AI-generated code patterns",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Application startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application components on startup."""
    logger.info("Starting Shadow AI Detection API...")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Don't fail startup if database init fails
    
    logger.info("Application startup complete")


# Request/Response models
class CodeAnalysisRequest(BaseModel):
    """Request model for code analysis."""
    code: str
    language: str = "auto"
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Code cannot be empty')
        if len(v) > 1000000:  # 1MB limit for text input
            raise ValueError('Code is too long (max 1MB)')
        return v


class AnalysisResult(BaseModel):
    """Response model for analysis results."""
    source: str
    language: str
    result: str
    confidence: float
    reason: str
    patterns_found: List[str]
    analysis_details: Dict[str, Any]
    warnings: List[str] = []


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    components: Dict[str, str]


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    details: str
    code: int


class QuizQuestion(BaseModel):
    """Response model for a single quiz question."""
    id: int
    question: str
    code: str
    language: str
    patterns: List[str]


class QuizAnswer(BaseModel):
    """Request model for quiz answer submission."""
    question_id: int
    user_answer: str  # "AI" or "Human"


class QuizResult(BaseModel):
    """Response model for quiz answer result."""
    question_id: int
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str
    patterns: List[str]


class QuizSummary(BaseModel):
    """Response model for quiz summary."""
    total_questions: int
    correct_answers: int
    score_percentage: float
    questions_attempted: List[int]


class HistoryRecord(BaseModel):
    """Response model for a single history record."""
    id: int
    filename: str
    timestamp: str
    formatted_timestamp: str
    result: str
    score: int
    language: str
    patterns: List[str]


class HistoryResponse(BaseModel):
    """Response model for history endpoint."""
    records: List[HistoryRecord]
    total_count: int


class StatsResponse(BaseModel):
    """Response model for statistics."""
    total_analyses: int
    results_breakdown: Dict[str, int]
    average_score: float
    recent_activity: int


# Helper functions
def format_analysis_result(analysis_data: Dict[str, Any], source: str, language: str) -> AnalysisResult:
    """
    Format analysis results into a standardized response.
    
    Args:
        analysis_data: Raw analysis results from the engine
        source: Source identifier (filename or "text_input")
        language: Detected or specified language
        
    Returns:
        Formatted AnalysisResult object
    """
    # Extract key metrics
    summary = analysis_data.get('summary', {})
    suspicion_score = summary.get('overall_suspicion_score', 0.0)
    risk_factors = summary.get('risk_factors', [])
    
    # Determine result verdict
    if suspicion_score >= 70.0:
        result_verdict = "Likely AI-Generated"
    elif suspicion_score >= 40.0:
        result_verdict = "Possibly AI-Generated"
    else:
        result_verdict = "Likely Human-Written"
    
    # Create reason from risk factors
    if risk_factors:
        primary_reasons = risk_factors[:2]  # Take first 2 reasons
        reason = ", ".join(primary_reasons)
        
        # Extract pattern names for patterns_found
        patterns_list = [factor.split('(')[0].strip() for factor in risk_factors]
    else:
        reason = "No significant AI patterns detected"
        patterns_list = []
    
    # Extract warnings from metadata
    metadata = analysis_data.get('analysis_metadata', {})
    warnings = metadata.get('errors_encountered', [])
    
    return AnalysisResult(
        source=source,
        language=language,
        result=result_verdict,
        confidence=round(suspicion_score, 1),
        reason=reason,
        patterns_found=patterns_list,
        analysis_details=analysis_data,
        warnings=warnings
    )


def handle_parser_error(error: Exception) -> HTTPException:
    """
    Convert parser errors to appropriate HTTP exceptions.
    
    Args:
        error: The parser exception
        
    Returns:
        HTTPException with appropriate status code and message
    """
    if isinstance(error, FileTooLargeError):
        return HTTPException(
            status_code=413,
            detail=f"File too large: {str(error)}"
        )
    elif isinstance(error, InvalidInputError):
        return HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(error)}"
        )
    elif isinstance(error, ParserError):
        return HTTPException(
            status_code=400,
            detail=f"Parser error: {str(error)}"
        )
    elif isinstance(error, FileNotFoundError):
        return HTTPException(
            status_code=404,
            detail="File not found"
        )
    elif isinstance(error, PermissionError):
        return HTTPException(
            status_code=403,
            detail="Permission denied accessing file"
        )
    else:
        return HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(error)}"
        )


# API Endpoints
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API status.
    
    Returns:
        Health status and component information
    """
    try:
        # Test basic functionality by running a minimal analysis
        test_code = "def test(): pass"
        test_analysis = analyze(test_code)
        engine_status = "ok" if test_analysis else "error"
    except Exception as e:
        logger.error(f"Health check failed for engine: {e}")
        engine_status = "error"
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        components={
            "api": "ok",
            "engine": engine_status,
            "parser": "ok"
        }
    )


@app.post("/api/check", response_model=AnalysisResult)
async def analyze_code_text(request: CodeAnalysisRequest):
    """
    Analyze raw code text for AI-generated patterns.
    
    Args:
        request: CodeAnalysisRequest containing code and optional language
        
    Returns:
        Analysis results with confidence score and detected patterns
        
    Raises:
        HTTPException: If analysis fails or input is invalid
    """
    try:
        logger.info(f"Analyzing code text (length: {len(request.code)} chars)")
        
        # Parse the code text
        parsed_results = parse(request.code)
        
        if not parsed_results:
            raise HTTPException(
                status_code=400,
                detail="No valid code content found in input"
            )
        
        # Analyze the first (and only) result
        result = parsed_results[0]
        content = result['content']
        detected_language = result['language']
        
        # Use specified language if provided and not "auto"
        final_language = request.language if request.language != "auto" else detected_language
        
        # Run the analysis
        analysis = analyze(content)
        
        # Format the response
        analysis_result = format_analysis_result(
            analysis, 
            "text_input", 
            final_language
        )
        
        # Log the analysis to database
        try:
            db = get_database()
            db.log_analysis(
                filename="text_input",
                result=analysis_result.result,
                score=int(analysis_result.confidence),
                language=final_language,
                patterns=analysis_result.patterns_found,
                analysis_data=analysis_result.analysis_details
            )
        except Exception as e:
            # Don't fail the API call if logging fails
            logger.warning(f"Failed to log analysis to database: {e}")
        
        logger.info(f"Analysis completed: {analysis_result.result} ({analysis_result.confidence}%)")
        return analysis_result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Handle Pydantic validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except (ParserError, InvalidInputError, FileTooLargeError) as e:
        raise handle_parser_error(e)
    except Exception as e:
        logger.error(f"Error analyzing code text: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during analysis: {str(e)}"
        )


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_uploaded_file(file: UploadFile = File(...)):
    """
    Analyze an uploaded code file for AI-generated patterns.
    
    Args:
        file: Uploaded file containing source code
        
    Returns:
        Analysis results with confidence score and detected patterns
        
    Raises:
        HTTPException: If analysis fails or file is invalid
    """
    try:
        logger.info(f"Analyzing uploaded file: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
        
        # Read file content
        content = await file.read()
        
        # Convert bytes to string
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text_content = content.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="File encoding not supported. Please use UTF-8 or Latin-1."
                )
        
        # Check file size (already limited by FastAPI, but double-check)
        if len(text_content) > 5_000_000:  # 5MB limit
            raise HTTPException(
                status_code=413,
                detail="File too large (max 5MB)"
            )
        
        # Parse the file content
        parsed_results = parse(text_content)
        
        if not parsed_results:
            raise HTTPException(
                status_code=400,
                detail="No valid code content found in file"
            )
        
        # Analyze the first (and only) result
        result = parsed_results[0]
        content = result['content']
        detected_language = result['language']
        
        # Run the analysis
        analysis = analyze(content)
        
        # Format the response
        analysis_result = format_analysis_result(
            analysis, 
            file.filename, 
            detected_language
        )
        
        # Log the analysis to database
        try:
            db = get_database()
            db.log_analysis(
                filename=file.filename,
                result=analysis_result.result,
                score=int(analysis_result.confidence),
                language=detected_language,
                patterns=analysis_result.patterns_found,
                analysis_data=analysis_result.analysis_details
            )
        except Exception as e:
            # Don't fail the API call if logging fails
            logger.warning(f"Failed to log analysis to database: {e}")
        
        logger.info(f"File analysis completed: {analysis_result.result} ({analysis_result.confidence}%)")
        return analysis_result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except (ParserError, InvalidInputError, FileTooLargeError) as e:
        raise handle_parser_error(e)
    except Exception as e:
        logger.error(f"Error analyzing uploaded file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during file analysis: {str(e)}"
        )


# Quiz functionality
@app.get("/api/quiz/questions", response_model=List[QuizQuestion])
async def get_quiz_questions():
    """
    Get all available quiz questions (without correct answers).
    
    Returns:
        List of quiz questions with code snippets and metadata
    """
    try:
        import json
        import os
        
        quiz_file_path = os.path.join("data", "quiz_questions.json")
        
        if not os.path.exists(quiz_file_path):
            raise HTTPException(
                status_code=404,
                detail="Quiz questions file not found"
            )
        
        with open(quiz_file_path, 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
        
        questions = []
        for q in quiz_data['quiz_questions']:
            # Don't include correct answer in the response
            question = QuizQuestion(
                id=q['id'],
                question=q['question'],
                code=q['code'],
                language=q['language'],
                patterns=q['patterns']
            )
            questions.append(question)
        
        logger.info(f"Served {len(questions)} quiz questions")
        return questions
        
    except Exception as e:
        logger.error(f"Error loading quiz questions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load quiz questions: {str(e)}"
        )


@app.post("/api/quiz/answer", response_model=QuizResult)
async def submit_quiz_answer(answer: QuizAnswer):
    """
    Submit an answer to a quiz question and get the result.
    
    Args:
        answer: QuizAnswer containing question ID and user's answer
        
    Returns:
        QuizResult with correct answer and explanation
    """
    try:
        import json
        import os
        
        quiz_file_path = os.path.join("data", "quiz_questions.json")
        
        if not os.path.exists(quiz_file_path):
            raise HTTPException(
                status_code=404,
                detail="Quiz questions file not found"
            )
        
        with open(quiz_file_path, 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
        
        # Find the question
        question_data = None
        for q in quiz_data['quiz_questions']:
            if q['id'] == answer.question_id:
                question_data = q
                break
        
        if not question_data:
            raise HTTPException(
                status_code=404,
                detail=f"Question with ID {answer.question_id} not found"
            )
        
        # Validate user answer
        if answer.user_answer not in ["AI", "Human"]:
            raise HTTPException(
                status_code=400,
                detail="Answer must be either 'AI' or 'Human'"
            )
        
        # Check if answer is correct
        correct_answer = question_data['correct_answer']
        is_correct = answer.user_answer == correct_answer
        
        result = QuizResult(
            question_id=answer.question_id,
            user_answer=answer.user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            explanation=question_data['explanation'],
            patterns=question_data['patterns']
        )
        
        logger.info(f"Quiz answer submitted: Q{answer.question_id}, "
                   f"User: {answer.user_answer}, Correct: {is_correct}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing quiz answer: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process quiz answer: {str(e)}"
        )


# History and Dashboard endpoints
@app.get("/api/history", response_model=HistoryResponse)
async def get_analysis_history(limit: int = 100):
    """
    Get analysis history from the database.
    
    Args:
        limit: Maximum number of records to return (default: 100, max: 1000)
        
    Returns:
        List of analysis history records
    """
    try:
        # Limit the maximum number of records to prevent memory issues
        if limit > 1000:
            limit = 1000
        elif limit < 1:
            limit = 1
        
        db = get_database()
        records = db.get_history(limit=limit)
        
        # Convert to Pydantic models
        history_records = []
        for record in records:
            history_record = HistoryRecord(
                id=record['id'],
                filename=record['filename'],
                timestamp=record['timestamp'],
                formatted_timestamp=record['formatted_timestamp'],
                result=record['result'],
                score=record['score'],
                language=record['language'] or 'unknown',
                patterns=record['patterns']
            )
            history_records.append(history_record)
        
        logger.info(f"Served {len(history_records)} history records")
        return HistoryResponse(
            records=history_records,
            total_count=len(history_records)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analysis history: {str(e)}"
        )


@app.get("/api/stats", response_model=StatsResponse)
async def get_analysis_stats():
    """
    Get analysis statistics from the database.
    
    Returns:
        Analysis statistics including totals and breakdowns
    """
    try:
        db = get_database()
        stats = db.get_stats()
        
        return StatsResponse(
            total_analyses=stats['total_analyses'],
            results_breakdown=stats['results_breakdown'],
            average_score=stats['average_score'],
            recent_activity=stats['recent_activity']
        )
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@app.get("/")
async def root():
    """
    Root endpoint redirects to the web interface.
    """
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')


@app.get("/dashboard")
async def dashboard():
    """
    Dashboard page for viewing analysis history.
    """
    from fastapi.responses import FileResponse
    return FileResponse('static/dashboard.html')


@app.get("/api")
async def api_info():
    """
    API information endpoint.
    """
    return {
        "message": "Shadow AI Detection API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors with custom response."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "details": f"The requested endpoint does not exist",
            "code": 404
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors with custom response."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": "An unexpected error occurred",
            "code": 500
        }
    )


# Development server runner
def run_dev_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """
    Run the development server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
    """
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_dev_server()
