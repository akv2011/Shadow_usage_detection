@echo off
REM Shadow AI Development Helper
REM Usage: dev.bat [command]

if "%1"=="test" (
    echo Running tests...
    conda run -n shadow-ai pytest
    goto :end
)

if "%1"=="lint" (
    echo Running linter...
    conda run -n shadow-ai ruff check .
    goto :end
)

if "%1"=="format" (
    echo Formatting code...
    conda run -n shadow-ai ruff format .
    goto :end
)

if "%1"=="types" (
    echo Checking types...
    conda run -n shadow-ai mypy shadow_ai
    goto :end
)

if "%1"=="all" (
    echo Running all checks...
    conda run -n shadow-ai ruff check .
    if %errorlevel% neq 0 goto :end
    conda run -n shadow-ai mypy shadow_ai
    if %errorlevel% neq 0 goto :end
    conda run -n shadow-ai pytest
    goto :end
)

if "%1"=="clean" (
    echo Cleaning cache files...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    del /s /q *.pyc 2>nul
    if exist ".pytest_cache" rd /s /q ".pytest_cache"
    if exist ".mypy_cache" rd /s /q ".mypy_cache"
    if exist "htmlcov" rd /s /q "htmlcov"
    echo Cache cleaned.
    goto :end
)

echo Shadow AI Development Helper
echo.
echo Available commands:
echo   dev test      - Run pytest
echo   dev lint      - Run ruff linting  
echo   dev format    - Format code with ruff
echo   dev types     - Run mypy type checking
echo   dev all       - Run all checks (lint + types + tests)
echo   dev clean     - Clean Python cache files
echo.
echo Make sure to activate the conda environment first:
echo   conda activate shadow-ai

:end
