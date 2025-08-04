# Shadow AI Detection Tool

A tool I built to detect AI-generated code patterns using heuristic analysis. After working with AI-generated code, I noticed certain patterns that kept showing up - generic variable names, overly perfect comments, uniform structure. So I decided to build something that could spot these patterns automatically.

[![CI](https://github.com/akv2011/Shadow_usage_detection/actions/workflows/ci.yml/badge.svg)](https://github.com/akv2011/Shadow_usage_detection/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What This Does

I built this because I kept seeing the same patterns in AI-generated code at work. You know how AI tends to use really generic variable names like `data`, `result`, `value`? Or how it writes these overly explanatory comments for simple things? This tool analyzes code and gives you a confidence score on whether it might be AI-generated.

**What it looks for:**
- Generic variable names everywhere
- Comments that sound like they're explaining code to a 5-year-old
- Code that's almost *too* uniform and perfect
- Sudden style changes within the same file (like someone copy-pasted AI code)

**How I use it:**
- Quick sanity check during code reviews
- Teaching people what AI code patterns look like
- Research into how AI actually writes code

## ✨ Features

### The Core Engine
- **🔍 Pattern Detection**: Spots those telltale AI patterns I keep seeing
- **🌳 Code Structure Analysis**: Looks at how the code is actually organized
- **📊 Confidence Scoring**: Gives you a percentage - higher means more likely AI
- **🎨 Style Detective**: Catches when someone mixes human and AI code in the same file

### Ways to Use It
- **💻 Command Line**: For when you want to automate things or check lots of files
- **🌐 Web Interface**: Easy drag-and-drop if you prefer clicking buttons
- **📋 History Dashboard**: See all your past analyses and spot trends
- **🧠 Quiz Mode**: I made this to help people learn what AI code looks like

### Under the Hood
- **🔤 Multi-Language**: Works with Python, JavaScript, Java, C++, and more
- **📁 Batch Processing**: Check entire folders at once
- **💾 Database**: Keeps track of everything you've analyzed
- **🔧 API**: Hook it up to your own tools

## 📊 What You Get

The tool gives you a straightforward analysis of your code:

### Command Line Results
```
Source: filename.py
Language: Python
Result: [What I think]
Confidence: [How sure I am]%
Reason: [Why I think that]
Patterns Found: [Specific things I spotted]
```

### How to Read the Results

**My Verdicts:**
- **"Likely Human-Written"** (0-39%): Looks pretty natural to me
- **"Possibly AI-Generated"** (40-69%): Some red flags, but could go either way
- **"Likely AI-Generated"** (70-100%): Yeah, this screams AI

**What I Look For:**
- Generic variable names (e.g., `data`, `result`, `value`)
- Overly uniform code structure
- Simplistic or repetitive comments
- AI-specific language patterns in comments
- Inconsistent coding styles within the same file

**About the Confidence Score:**
- Higher scores mean I'm more confident it's AI-generated
- I use multiple detection methods and combine them
- It's not perfect, but it's pretty good at spotting the obvious stuff

## 🚀 Getting Started

### What You Need
- Python 3.9 or newer
- Git (to download this)
- A few minutes of your time

### Quick Setup

1. **Grab the Code**
   ```bash
   git clone https://github.com/akv2011/Shadow_usage_detection.git
   cd Shadow_usage_detection
   ```

2. **Set Up Your Environment**
   
   I prefer conda, but pip works too:
   ```bash
   # Using conda (my preference)
   conda create -n shadow-ai python=3.11 -y
   conda activate shadow-ai
   
   # Or using pip
   python -m venv shadow-ai-env
   # Then activate it (Windows: shadow-ai-env\Scripts\activate)
   ```

3. **Install Everything**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Test It Out**
   ```bash
   # Quick test
   echo "def test(): pass" > test.py
   python -m shadow_ai.cli analyze test.py
   ```

## 💻 How to Use It

### Command Line (My Favorite Way)

#### Check a Single File
```bash
python -m shadow_ai.cli analyze your_file.py
```

You'll get something like:
```
Source: your_file.py
Language: Python
Result: Likely Human-Written
Confidence: 15.3%
Reason: High structural uniformity, Generic variable names
Patterns Found: [High structural uniformity, Generic variable names]
```

#### Analyze Code Directly
```bash
python -m shadow_ai.cli check --text "def hello(): print('Hello World')"
```

#### Scan a Whole Directory
```bash
# Check up to 5 files in current directory
python -m shadow_ai.cli scan . --max-files 5

# Or scan a specific project
python -m shadow_ai.cli scan /path/to/project --max-files 10
```

### Web Interface (For the GUI Folks)

1. **Start the Server**
   ```bash
   python main.py
   ```

2. **Open Your Browser**
   Go to `http://127.0.0.1:8000`

3. **What You Can Do:**
   - **Main Page**: Upload files or paste code for instant analysis
   - **Dashboard** (`/dashboard`): See your analysis history and stats
   - **Quiz** (`/quiz.html`): Learn about AI code patterns

### API (For the Developers)

I built a REST API if you want to integrate this into your own tools:

```python
import requests

response = requests.post('http://127.0.0.1:8000/api/check', 
                        json={'code': 'def hello(): pass', 'language': 'python'})
result = response.json()
print(f"Result: {result['result']} ({result['confidence']}%)")
```

Available endpoints:
- `POST /api/check` - Analyze text
- `POST /api/analyze` - Analyze uploaded file
- `GET /api/history` - Get your analysis history
- `GET /api/stats` - Get statistics

## 🚀 Development Setup

If you want to tinker with the code or add your own detection patterns, here's how I set up my development environment:

### Get Started
```bash
# Clone and install for development
git clone https://github.com/yourusername/shadow_usage_detection.git
cd shadow_usage_detection
pip install -e ".[dev]"

# Activate your environment and run
conda activate shadow-ai  # or your preferred method
python main.py
```

### My Quality Checks

I'm pretty particular about code quality, so here's what I use:

```bash
# Run everything at once (my preference)
./dev.bat all       # Windows
./scripts/dev.ps1   # PowerShell alternative

# Or run things individually:
pytest                    # Tests (try to keep these passing!)
pytest --cov=shadow_ai   # Coverage (I aim for high coverage)
ruff check .             # Linting
ruff format .            # Auto-formatting
mypy shadow_ai           # Type checking
```

### How I Organized Things

```
shadow_ai/              # Where the magic happens
├── engine.py           # Core detection logic (most fun to work on)
├── parser.py           # Handles different file types
├── cli.py              # Command-line interface
├── scoring.py          # Confidence algorithms
└── database.py         # SQLite operations

static/                 # Web interface
├── index.html          # Main analyzer page
├── dashboard.html      # History dashboard
└── quiz.html           # Interactive learning tool

tests/                  # Comprehensive test suite
├── test_*.py           # All the tests
└── __init__.py

main.py                 # FastAPI server
```

### Adding New Detection Patterns

Found a new AI pattern I missed? Here's how to add it:

1. **Add the logic** in `shadow_ai/engine.py` (look for the `analyze_patterns` method)
2. **Write tests** in `tests/test_engine.py` 
3. **Adjust scoring** in `shadow_ai/scoring.py` if needed
4. **Run the tests** to make sure I didn't break anything

I love finding new patterns - AI tools keep evolving, so there's always something new to catch!

## 🧪 Testing

I'm pretty thorough with testing - figured if I'm going to detect patterns, I better make sure my own code works properly:

### What I Test
- **Unit Tests**: Every core function and method
- **Integration Tests**: Real API calls and CLI commands  
- **Pattern Detection**: All the heuristics with known examples
- **Style Detection**: Edge cases for inconsistency detection

### Running Tests
```bash
# Run everything (what I usually do)
pytest

# Check how much I'm actually testing
pytest --cov=shadow_ai --cov-report=html

# Test specific parts when I'm working on them
pytest tests/test_engine.py
pytest tests/test_api.py
```

## ⚙️ Configuration

I use `pyproject.toml` for everything - keeps it all in one place:

- **Ruff**: For fast linting and formatting (way faster than the old tools)
- **Mypy**: Type checking with strict settings (catches bugs early)
- **Pytest**: Testing with coverage (gotta know what I'm missing)
- **Build System**: Modern Python packaging

## 📈 Project Status

**Completion: 100%** 🎉

Everything I wanted to build is working:

- ✅ **Core Detection Engine** - All the pattern-matching logic
- ✅ **Multi-Language Support** - Python, JavaScript, Java, etc.
- ✅ **CLI Interface** - Command-line tool for quick checks
- ✅ **Web Interface** - Nice UI for those who prefer clicking
- ✅ **Confidence Scoring** - Numbers to back up the analysis
- ✅ **Interactive Quiz** - Learn what patterns look like
- ✅ **Style Detection** - Spots inconsistent coding styles
- ✅ **Database History** - Keeps track of all analyses
- ✅ **Dashboard** - See trends and statistics
- ✅ **Comprehensive Tests** - High coverage, reliable code
- ✅ **Documentation** - This README and inline comments

## � What's Next?

I've got some ideas for making this even better:

- **Machine Learning**: Maybe train some models on labeled datasets
- **More Languages**: Add support for languages I haven't covered yet  
- **Better Visualizations**: Make the dashboard even more insightful
- **Enterprise Features**: User accounts and API keys if people want that
- **Plugin System**: Let others add their own detection algorithms

## 🤝 Want to Help?

I'd love to have others contribute! Here's how:

### Quick Start for Contributors
```bash
# Fork my repo, then:
git clone https://github.com/yourusername/Shadow_usage_detection.git
conda create -n shadow-ai-dev python=3.11 -y
conda activate shadow-ai-dev
pip install -e ".[dev]"
```

### Making Changes
1. **Create a branch** for your feature
2. **Follow my code style** (Ruff handles most of it)
3. **Add tests** for anything new
4. **Run the quality checks** (`./dev.bat` or `pytest && ruff check .`)
5. **Submit a pull request**

I'm pretty responsive to PRs, especially if they include tests!

## 📚 Documentation

### What's Available
- **[Environment Setup](docs/environment.md)** - If you need more detailed setup info
- **Interactive API Docs** - Start the server and visit `/docs` 
- **This README** - Which hopefully explains everything

### API Documentation
When you run `python main.py`, check out:
- `http://127.0.0.1:8000/docs` - Swagger UI (my favorite)
- `http://127.0.0.1:8000/redoc` - Alternative format

## � License

MIT License - basically, use it however you want. See the [LICENSE](LICENSE) file for the legal stuff.

## 🙏 Thanks

Shoutout to the tools that made this possible:
- **Python's AST module** - For making code analysis accessible
- **FastAPI** - Such a nice web framework
- **Ruff** - Finally, fast Python tooling
- **Everyone in the open source community** - Y'all are awesome

## � Need Help?

If something's not working or you have questions:

1. **Check this README first** - I tried to cover the common stuff
2. **Look through GitHub issues** - Someone might have had the same problem
3. **Open a new issue** - I'll try to help out
4. **Start a discussion** - For general questions or ideas

## 🎓 A Note on Usage

I built this as a learning tool and to satisfy my own curiosity about AI code patterns. It's meant to:

- **Help you learn** what AI-generated code looks like
- **Support code reviews** with additional insights  
- **Enable research** into AI-generated content

Remember: this tool gives you data points, but human judgment is still the most important factor. Use it as one tool among many!

---

**Built with curiosity, caffeine, and a lot of Python** ☕
