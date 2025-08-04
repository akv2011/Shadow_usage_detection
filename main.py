
import io
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
import uvicorn

from shadow_ai.engine import analyze
from shadow_ai.parser import parse, ParserError, InvalidInputError, FileTooLargeError
from shadow_ai.database import init_database, get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Shadow AI Detection API",
    description="Heuristic-based tool for detecting AI-generated code patterns",
    version="0.1.0",
    docs_url="/docs",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Shadow AI Detection API...")

    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    logger.info("Application startup complete")


class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "auto"

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Code cannot be empty')
        if len(v) > 1000000:
            raise ValueError('Code is too long (max 1MB)')
        return v


class AnalysisResult(BaseModel):
    source: str
    language: str
    result: str
    confidence: float
    reason: str
    patterns_found: List[str]
    analysis_details: Dict[str, Any]
    warnings: List[str] = []


class HealthResponse(BaseModel):
    status: str
    version: str
    components: Dict[str, str]


class ErrorResponse(BaseModel):
    error: str
    details: str
    code: int


class QuizQuestion(BaseModel):
    id: int
    question: str
    code: str
    language: str
    patterns: List[str]


class QuizAnswer(BaseModel):

    question_id: int
    user_answer: str


class QuizResult(BaseModel):

    question_id: int
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str
    patterns: List[str]


class QuizSummary(BaseModel):

    total_questions: int
    correct_answers: int
    score_percentage: float
    questions_attempted: List[int]


class HistoryRecord(BaseModel):

    id: int
    filename: str
    timestamp: str
    formatted_timestamp: str
    result: str
    score: int
    language: str
    patterns: List[str]


class HistoryResponse(BaseModel):

    records: List[HistoryRecord]
    total_count: int


class StatsResponse(BaseModel):

    total_analyses: int
    results_breakdown: Dict[str, int]
    average_score: float
    recent_activity: int


def format_analysis_result(analysis_data: Dict[str, Any], source: str, language: str) -> AnalysisResult:

    # Extract key metrics
    summary = analysis_data.get('summary', {})
    suspicion_score = summary.get('overall_suspicion_score', 0.0)
    risk_factors = summary.get('risk_factors', [])

    if suspicion_score >= 70.0:
        result_verdict = "Likely AI-Generated"
    elif suspicion_score >= 40.0:
        result_verdict = "Possibly AI-Generated"
    else:
        result_verdict = "Likely Human-Written"

    if risk_factors:
        primary_reasons = risk_factors[:2]
        reason = ", ".join(primary_reasons)

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


@app.get("/api/health", response_model=HealthResponse)
async def health_check():

    try:
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

    try:
        logger.info(f"Analyzing code text (length: {len(request.code)} chars)")

    # Parse the code text
        parsed_results = parse(request.code)

        if not parsed_results:
            raise HTTPException(
                status_code=400,
                detail="No valid code content found in input"
            )

        result = parsed_results[0]
        content = result['content']
        detected_language = result['language']

        final_language = request.language if request.language != "auto" else detected_language

        analysis = analyze(content)

        analysis_result = format_analysis_result(
            analysis, 
            "text_input", 
            final_language
        )

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
            logger.warning(f"Failed to log analysis to database: {e}")

        logger.info(f"Analysis completed: {analysis_result.result} ({analysis_result.confidence}%)")
        return analysis_result

    except HTTPException:
        raise
    except ValueError as e:
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

    try:
        logger.info(f"Analyzing uploaded file: {file.filename}")

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )

        content = await file.read()

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

        if len(text_content) > 5_000_000:
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

        result = parsed_results[0]
        content = result['content']
        detected_language = result['language']

        analysis = analyze(content)

        analysis_result = format_analysis_result(
            analysis, 
            file.filename, 
            detected_language
        )

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
            logger.warning(f"Failed to log analysis to database: {e}")

        logger.info(f"File analysis completed: {analysis_result.result} ({analysis_result.confidence}%)")
        return analysis_result

    except HTTPException:
        raise
    except (ParserError, InvalidInputError, FileTooLargeError) as e:
        raise handle_parser_error(e)
    except Exception as e:
        logger.error(f"Error analyzing uploaded file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during file analysis: {str(e)}"
        )


@app.get("/api/quiz/questions", response_model=List[QuizQuestion])
async def get_quiz_questions():

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


@app.get("/api/history", response_model=HistoryResponse)
async def get_analysis_history(limit: int = 100):

    try:
        if limit > 1000:
            limit = 1000
        elif limit < 1:
            limit = 1

        db = get_database()
        records = db.get_history(limit=limit)

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

    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')


@app.get("/dashboard")
async def dashboard():

    from fastapi.responses import FileResponse
    return FileResponse('static/dashboard.html')


@app.get("/api")
async def api_info():

    return {
        "message": "Shadow AI Detection API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):

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

    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": "An unexpected error occurred",
            "code": 500
        }
    )


def run_dev_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_dev_server()
