# Shadow AI Detection Tool

A heuristic-based tool for detecting AI-generated code patterns using advanced static analysis techniques.

[![CI](https://github.com/akv2011/Shadow_usage_detection/actions/workflows/ci.yml/badge.svg)](https://github.com/akv2011/Shadow_usage_detection/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/akv2011/Shadow_usage_detection/branch/main/graph/badge.svg)](https://codecov.io/gh/akv2011/Shadow_usage_detection)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

Shadow AI Detection Tool analyzes code snippets and files to identify patterns that may indicate AI-generated content. It uses a combination of heuristic checks, AST analysis, and pattern recognition to provide confidence scores and detailed analysis reports.

## ✨ Features

- **Multi-language Support**: Analyze code in various programming languages
- **Heuristic Detection**: Advanced pattern recognition for AI-generated code signatures
- **CLI Interface**: Easy-to-use command-line tool for batch processing
- **Web Interface**: Simple web UI for interactive analysis
- **Confidence Scoring**: Quantitative assessment (0-100%) with risk levels
- **Batch Processing**: Analyze multiple files and directories
- **Educational Quiz**: Interactive tool to learn about AI code patterns

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/akv2011/Shadow_usage_detection.git
cd Shadow_usage_detection

# Create and activate conda environment
conda create -n shadow-ai python=3.11 -y
conda activate shadow-ai

# Install the package
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Analyze a single file
shadow-ai analyze path/to/code.py

# Analyze a directory
shadow-ai batch path/to/project/

# Start web interface
shadow-ai web

# Run interactive quiz
shadow-ai quiz
```

## 🏗️ Development

### Environment Setup

```bash
# Activate environment
conda activate shadow-ai

# Run tests
pytest

# Run all quality checks
./dev.bat all  # Windows
# or use individual commands:
./dev.bat lint      # Run linting
./dev.bat format    # Format code
./dev.bat types     # Type checking
./dev.bat test      # Run tests
```

### Project Structure

```
shadow_ai/           # Main package
├── engine/          # Detection engine
├── cli/             # Command-line interface
├── api/             # Web API
└── utils/           # Utilities

tests/               # Test suite
docs/                # Documentation
scripts/             # Development scripts
```

## 🧪 Testing

The project maintains 100% test coverage with comprehensive test suites:

- **Unit Tests**: Core functionality testing
- **Integration Tests**: API and CLI testing  
- **Security Tests**: Vulnerability scanning
- **Performance Tests**: Benchmarking and optimization

## 🔧 Configuration

The project uses modern Python tooling configured in `pyproject.toml`:

- **Ruff**: Lightning-fast linting and formatting
- **Mypy**: Static type checking
- **Pytest**: Testing framework with coverage
- **Pre-commit**: Automated quality checks

## 📊 CI/CD Pipeline

Automated workflows using GitHub Actions:

- **Continuous Integration**: Multi-Python version testing (3.9-3.12)
- **Code Quality**: Linting, formatting, and type checking
- **Security Scanning**: Vulnerability detection with Bandit and Safety
- **Coverage Reporting**: Automated coverage tracking with Codecov
- **Dependency Updates**: Automated dependency management with Dependabot

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure all tests pass and coverage remains at 100%.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python best practices
- Powered by AST analysis and heuristic detection
- Inspired by the need for AI code transparency

## 📚 Documentation

For detailed documentation, see the [docs/](docs/) directory:

- [Environment Setup](docs/environment.md)
- [API Reference](docs/api.md) (coming soon)
- [Development Guide](docs/development.md) (coming soon)

## 🚧 Roadmap

- [ ] Core heuristic detection engine
- [ ] Multi-language file parser
- [ ] CLI interface implementation
- [ ] Web interface development
- [ ] Confidence scoring algorithm
- [ ] Interactive educational quiz
- [ ] Code style inconsistency detector
- [ ] SQLite database integration
- [ ] Comprehensive documentation

## 📈 Status

This project is in active development. Current progress:

- ✅ Project structure and CI/CD pipeline
- 🔄 Core detection engine (in progress)
- ⏳ CLI interface (planned)
- ⏳ Web interface (planned)
