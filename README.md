# Shadow AI Detection Tool

A comprehensive heuristic-based tool for detecting AI-generated code patterns using advanced static analysis techniques. This tool helps developers, educators, and code reviewers identify potentially AI-generated content in codebases.

[![CI](https://github.com/akv2011/Shadow_usage_detection/actions/workflows/ci.yml/badge.svg)](https://github.com/akv2011/Shadow_usage_detection/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/akv2011/Shadow_usage_detection/branch/main/graph/badge.svg)](https://codecov.io/gh/akv2011/Shadow_usage_detection)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Overview

Shadow AI Detection Tool is a production-ready application that analyzes source code to identify patterns commonly associated with AI-generated content. Using a sophisticated combination of heuristic analysis, Abstract Syntax Tree (AST) parsing, and pattern recognition algorithms, it provides quantitative assessments of code authenticity.

**Key Capabilities:**
- **Heuristic Analysis**: Detects generic variable names, simplistic comment patterns, and uniform code structures
- **Style Inconsistency Detection**: Identifies sudden changes in coding style that may indicate AI injection
- **Multi-Interface Support**: Available as both a command-line tool and web application
- **Educational Components**: Interactive quiz to help users learn about AI code patterns
- **Analysis History**: SQLite-based persistence layer for tracking analysis results over time

**Use Cases:**
- Code review processes in software development
- Academic integrity verification in educational settings
- Quality assurance in collaborative development environments
- Research into AI-generated code characteristics

## ✨ Features

### Core Detection Engine
- **🔍 Heuristic Pattern Detection**: Advanced algorithms for identifying AI-generated code signatures
- **🌳 AST Analysis**: Deep structural analysis using Python's Abstract Syntax Tree module
- **📊 Confidence Scoring**: Quantitative assessment with percentage scores and risk levels
- **🎨 Style Inconsistency Detection**: Identifies abrupt changes in coding patterns within files

### User Interfaces
- **💻 Command-Line Interface**: Full-featured CLI for automation and batch processing
- **🌐 Web Interface**: Interactive web application with drag-and-drop file upload
- **📋 Analysis Dashboard**: Historical analysis tracking with statistics and visualizations
- **🧠 Interactive Quiz**: Educational tool for learning AI code pattern recognition

### Technical Features
- **🔤 Multi-Language Support**: Analyzes code in Python, JavaScript, Java, C++, and more
- **📁 Batch Processing**: Efficient analysis of multiple files and directories
- **💾 Data Persistence**: SQLite database for storing analysis history and statistics
- **🔧 RESTful API**: FastAPI-based backend for integration with other tools

## 📊 Output Format

The tool provides detailed analysis results in a standardized format:

### CLI Output Format
```
Source: filename.py
Language: Python
Result: [Verdict]
Confidence: [Score]%
Reason: [Primary detected patterns]
Patterns Found: [List of specific patterns detected]
```

### Result Interpretations

**Verdict Types:**
- **"Likely Human-Written"** (0-39% confidence): Code shows natural human patterns
- **"Possibly AI-Generated"** (40-69% confidence): Some suspicious patterns detected
- **"Likely AI-Generated"** (70-100% confidence): Strong indicators of AI generation

**Common Detected Patterns:**
- Generic variable names (e.g., `data`, `result`, `value`)
- Overly uniform code structure
- Simplistic or repetitive comments
- AI-specific language patterns in comments
- Inconsistent coding styles within the same file

**Confidence Score Factors:**
- Higher scores indicate stronger evidence of AI generation
- Scores are calculated using weighted heuristic results
- Multiple detection methods contribute to the final assessment

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Git (for cloning the repository)
- Conda (recommended) or pip for package management

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/akv2011/Shadow_usage_detection.git
   cd Shadow_usage_detection
   ```

2. **Set Up Python Environment**
   
   **Option A: Using Conda (Recommended)**
   ```bash
   # Create a new conda environment
   conda create -n shadow-ai python=3.11 -y
   conda activate shadow-ai
   ```
   
   **Option B: Using venv**
   ```bash
   # Create virtual environment
   python -m venv shadow-ai-env
   
   # Activate (Windows)
   shadow-ai-env\Scripts\activate
   
   # Activate (macOS/Linux)
   source shadow-ai-env/bin/activate
   ```

3. **Install the Package**
   ```bash
   # Install the package with all dependencies
   pip install -e ".[dev]"
   ```

4. **Verify Installation**
   ```bash
   # Test the CLI
   python -m shadow_ai.cli --help
   
   # Test a quick analysis
   echo "def test(): pass" > test.py
   python -m shadow_ai.cli analyze test.py
   ```

## 💻 Usage

### Command-Line Interface (CLI)

The CLI provides three main commands for different analysis scenarios:

#### 1. Analyze a Single File
```bash
python -m shadow_ai.cli analyze <filename>
```

**Example:**
```bash
python -m shadow_ai.cli analyze my_script.py
```

**Output:**
```
Source: my_script.py
Language: Python
Result: Likely Human-Written
Confidence: 15.3%
Reason: High structural uniformity, Generic variable names
Patterns Found: [High structural uniformity, Generic variable names]
```

#### 2. Analyze Raw Code Text
```bash
python -m shadow_ai.cli check --text "your code here"
```

**Example:**
```bash
python -m shadow_ai.cli check --text "def hello(): print('Hello World')"
```

#### 3. Scan a Directory
```bash
python -m shadow_ai.cli scan <directory> [--max-files N]
```

**Example:**
```bash
# Scan current directory, analyze up to 5 files
python -m shadow_ai.cli scan . --max-files 5

# Scan project directory
python -m shadow_ai.cli scan /path/to/project --max-files 10
```

### Web Interface

The web interface provides an intuitive way to analyze code through your browser.

#### 1. Start the Web Server
```bash
python main.py
```

The server will start on `http://127.0.0.1:8000`

#### 2. Access the Application
- **Main Analyzer**: `http://127.0.0.1:8000/` - Upload files or paste code
- **Analysis Dashboard**: `http://127.0.0.1:8000/dashboard` - View analysis history and statistics
- **Interactive Quiz**: `http://127.0.0.1:8000/quiz.html` - Learn about AI code patterns

#### 3. Web Interface Features
- **Text Input**: Paste code directly into the text area
- **File Upload**: Drag and drop or browse to upload code files
- **Real-time Analysis**: Instant results with detailed pattern breakdowns
- **History Tracking**: All analyses are automatically saved to the database
- **Statistics Dashboard**: View analysis trends and patterns over time

### API Endpoints

For programmatic access, the tool provides RESTful API endpoints:

#### Analysis Endpoints
- `POST /api/check` - Analyze text input
- `POST /api/analyze` - Analyze uploaded file
- `GET /api/history` - Get analysis history
- `GET /api/stats` - Get analysis statistics

#### Quiz Endpoints
- `GET /api/quiz/questions` - Get quiz questions
- `POST /api/quiz/answer` - Submit quiz answers

**Example API Usage:**
```python
import requests

# Analyze code text
response = requests.post('http://127.0.0.1:8000/api/check', 
                        json={'code': 'def hello(): pass', 'language': 'python'})
result = response.json()
print(f"Result: {result['result']} ({result['confidence']}%)")
```

## 🏗️ Development

### Development Environment Setup

```bash
# Activate your environment
conda activate shadow-ai  # or source shadow-ai-env/bin/activate

# Install development dependencies (already included with -e ".[dev]")
pip install -e ".[dev]"

# Run the development server with auto-reload
python main.py
```

### Quality Assurance

The project uses modern Python tooling for code quality:

```bash
# Run all quality checks
./dev.bat all       # Windows
./scripts/dev.ps1   # PowerShell alternative

# Individual commands:
pytest                    # Run tests
pytest --cov=shadow_ai   # Run tests with coverage
ruff check .             # Linting
ruff format .            # Code formatting
mypy shadow_ai           # Type checking
```

### Project Structure

```
shadow_ai/              # Main package
├── __init__.py         # Package initialization
├── engine.py           # Core detection engine
├── parser.py           # Multi-language file parser
├── cli.py              # Command-line interface
├── scoring.py          # Confidence scoring algorithms
└── database.py         # SQLite database management

static/                 # Web interface files
├── index.html          # Main analyzer page
├── dashboard.html      # Analysis history dashboard
└── quiz.html           # Interactive quiz

tests/                  # Comprehensive test suite
├── test_*.py           # Unit and integration tests
└── __init__.py

main.py                 # FastAPI web server
pyproject.toml          # Project configuration
README.md               # This documentation
```

## 🧪 Testing

The project maintains comprehensive test coverage with multiple test types:

- **Unit Tests**: Core functionality testing for all modules
- **Integration Tests**: API and CLI testing with real scenarios
- **Heuristic Tests**: Validation of detection algorithms
- **Style Detection Tests**: Style inconsistency detector validation

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=shadow_ai --cov-report=html

# Run specific test modules
pytest tests/test_engine.py
pytest tests/test_api.py
```

## 🔧 Configuration

The project uses `pyproject.toml` for all configuration:

- **Ruff**: Fast linting and formatting
- **Mypy**: Static type checking with strict settings
- **Pytest**: Testing framework with coverage reporting
- **Build System**: Modern Python packaging with setuptools

## 📊 CI/CD Pipeline

Automated workflows ensure code quality:

- **Continuous Integration**: Multi-Python version testing (3.9-3.12)
- **Code Quality**: Automated linting, formatting, and type checking
- **Security Scanning**: Vulnerability detection
- **Test Coverage**: Automated coverage reporting
- **Dependency Management**: Automated dependency updates

## 📈 Current Status

**Project Completion: 100%** 🎉

All major features are implemented and tested:

- ✅ **Core Detection Engine** - Heuristic analysis with AST parsing
- ✅ **Multi-Language Parser** - Support for multiple programming languages
- ✅ **CLI Interface** - Full command-line functionality
- ✅ **Web Interface** - Interactive web application
- ✅ **Confidence Scoring** - Quantitative assessment algorithms
- ✅ **Interactive Quiz** - Educational tool for pattern recognition
- ✅ **Style Inconsistency Detector** - Advanced pattern detection
- ✅ **Database Integration** - SQLite-based analysis history
- ✅ **Analysis Dashboard** - Historical data visualization
- ✅ **Comprehensive Documentation** - User and developer guides
- ✅ **Test Suite** - High-coverage testing framework

## 🚧 Future Enhancements

Potential areas for future development:

- **Machine Learning Integration**: Train ML models on labeled datasets
- **Additional Language Support**: Expand beyond current language set
- **Advanced Visualization**: Enhanced dashboard analytics
- **Enterprise Features**: User management and API authentication
- **Plugin Architecture**: Extensible detection algorithm framework

## 🤝 Contributing

We welcome contributions to improve the Shadow AI Detection Tool! Here's how to get involved:

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/Shadow_usage_detection.git
   ```

2. **Set Up Development Environment**
   ```bash
   conda create -n shadow-ai-dev python=3.11 -y
   conda activate shadow-ai-dev
   pip install -e ".[dev]"
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Make Your Changes**
   - Follow the existing code style (Ruff formatting)
   - Add tests for new functionality
   - Update documentation as needed

5. **Run Quality Checks**
   ```bash
   pytest --cov=shadow_ai    # Ensure tests pass
   ruff check .              # Check code style
   mypy shadow_ai            # Verify type hints
   ```

6. **Submit Your Pull Request**
   ```bash
   git commit -m 'Add amazing feature'
   git push origin feature/amazing-feature
   ```

Please ensure all tests pass and maintain the high code coverage standards.

## 📚 Documentation

### Available Documentation

- **[Environment Setup Guide](docs/environment.md)** - Detailed environment configuration
- **API Reference** - RESTful API documentation (via `/docs` endpoint)
- **Development Guide** - Contributing and development practices

### Interactive Documentation

When running the web server, visit:
- `http://127.0.0.1:8000/docs` - Interactive API documentation (Swagger UI)
- `http://127.0.0.1:8000/redoc` - Alternative API documentation (ReDoc)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Python AST Module**: For enabling deep code structure analysis
- **FastAPI**: For the high-performance web framework
- **Ruff**: For lightning-fast code linting and formatting
- **The Open Source Community**: For inspiration and best practices

## 📞 Support

If you encounter issues or have questions:

1. **Check the Documentation**: Review this README and the docs folder
2. **Search Existing Issues**: Look through GitHub issues for similar problems
3. **Create a New Issue**: Provide detailed information about your problem
4. **Join Discussions**: Participate in GitHub Discussions for general questions

## 🎓 Educational Use

This tool is designed to be educational and help users understand AI-generated code patterns. It should be used as:

- **A learning tool** for understanding AI code characteristics
- **A supplementary check** in code review processes
- **A research tool** for studying AI-generated content

**Note**: While the tool provides valuable insights, human judgment should always be the final arbiter in determining code authenticity.

---

**Built with ❤️ using modern Python practices and open-source technologies.**
