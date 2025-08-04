# Development Scripts for Shadow AI Detection Tool
# Run these commands from the project root directory

# Activate the conda environment first:
# conda activate shadow-ai

# Code Quality Checks
function Test-Code {
    Write-Host "Running tests..." -ForegroundColor Green
    conda run -n shadow-ai pytest
}

function Check-Lint {
    Write-Host "Running linter..." -ForegroundColor Green
    conda run -n shadow-ai ruff check .
}

function Format-Code {
    Write-Host "Formatting code..." -ForegroundColor Green
    conda run -n shadow-ai ruff format .
}

function Check-Types {
    Write-Host "Checking types..." -ForegroundColor Green
    conda run -n shadow-ai mypy shadow_ai
}

function Test-All {
    Write-Host "Running all checks..." -ForegroundColor Green
    Check-Lint
    if ($LASTEXITCODE -eq 0) {
        Check-Types
        if ($LASTEXITCODE -eq 0) {
            Test-Code
        }
    }
}

function Install-Dev {
    Write-Host "Installing in development mode..." -ForegroundColor Green
    conda run -n shadow-ai pip install -e .
}

function Clean-Cache {
    Write-Host "Cleaning Python cache files..." -ForegroundColor Green
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Recurse -File -Name "*.pyc" | Remove-Item -Force
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
    if (Test-Path ".mypy_cache") { Remove-Item -Recurse -Force ".mypy_cache" }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
}

# Export functions for use
Export-ModuleMember -Function Test-Code, Check-Lint, Format-Code, Check-Types, Test-All, Install-Dev, Clean-Cache

Write-Host "Shadow AI Development Scripts Loaded!" -ForegroundColor Cyan
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  Test-Code      - Run pytest" 
Write-Host "  Check-Lint     - Run ruff linting"
Write-Host "  Format-Code    - Format code with ruff"
Write-Host "  Check-Types    - Run mypy type checking"
Write-Host "  Test-All       - Run all checks (lint + types + tests)"
Write-Host "  Install-Dev    - Install project in development mode"
Write-Host "  Clean-Cache    - Clean Python cache files"
