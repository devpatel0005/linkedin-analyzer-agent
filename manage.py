"""
Development task runner for LinkedIn Analyzer Agent
Simple script to run common development tasks
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description, shell=True):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=shell, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def setup_environment():
    """Setup development environment"""
    print("🚀 Setting up development environment...")
    
    tasks = [
        ("python setup.py", "Running setup script"),
    ]
    
    for command, description in tasks:
        if not run_command(command, description):
            return False
    
    return True


def run_server():
    """Start the development server"""
    print("🌐 Starting development server...")
    
    # Check if virtual environment is activated
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  Virtual environment not detected")
        print("Please activate your virtual environment first:")
        if os.name == 'nt':  # Windows
            print("  venv\\Scripts\\activate")
        else:
            print("  source venv/bin/activate")
        return False
    
    return run_command("python app.py", "Starting server")


def run_tests():
    """Run all tests"""
    print("🧪 Running tests...")
    
    # Try pytest first, fall back to basic tests
    commands = [
        ("python -m pytest test_basic.py -v", "Running pytest"),
        ("python test_basic.py", "Running basic tests")
    ]
    
    for command, description in commands:
        if run_command(command, description):
            return True
    
    return False


def lint_code():
    """Run code linting"""
    print("🔍 Linting code...")
    
    # Check if flake8 is available
    try:
        subprocess.run(["python", "-m", "flake8", "--version"], 
                      capture_output=True, check=True)
        return run_command("python -m flake8 src/ --max-line-length=100", 
                          "Running flake8")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  flake8 not available, skipping linting")
        print("Install with: pip install flake8")
        return True


def format_code():
    """Format code with black"""
    print("🎨 Formatting code...")
    
    try:
        subprocess.run(["python", "-m", "black", "--version"], 
                      capture_output=True, check=True)
        return run_command("python -m black src/ --line-length=100", 
                          "Running black formatter")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  black not available, skipping formatting")
        print("Install with: pip install black")
        return True


def clean_project():
    """Clean project files"""
    print("🧹 Cleaning project...")
    
    patterns_to_clean = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.egg-info",
        ".pytest_cache",
        "*.log"
    ]
    
    import shutil
    import glob
    
    for pattern in patterns_to_clean:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"  Removed directory: {path}")
                else:
                    os.remove(path)
                    print(f"  Removed file: {path}")
            except Exception as e:
                print(f"  Could not remove {path}: {e}")
    
    print("✅ Project cleaned")
    return True


def install_deps():
    """Install/update dependencies"""
    print("📦 Installing dependencies...")
    
    commands = [
        ("python -m pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing requirements"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def generate_docs():
    """Generate documentation"""
    print("📚 Generating documentation...")
    
    # Create a simple documentation structure
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Generate API documentation
    api_doc = docs_dir / "api.md"
    with open(api_doc, 'w') as f:
        f.write("""# LinkedIn Analyzer Agent API Documentation

## Overview
REST API for LinkedIn profile analysis and data extraction.

## Base URL
- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication
Currently no authentication required for development.

## Endpoints

### Health Check
```
GET /health
```
Returns service health status.

### Profile Scraping
```
POST /api/v1/profiles/scrape
```
Scrape a LinkedIn profile.

**Parameters:**
- `profile_url` (string): LinkedIn profile URL

### Batch Scraping
```
POST /api/v1/profiles/batch-scrape
```
Scrape multiple LinkedIn profiles.

**Parameters:**
- `profile_urls` (array): List of LinkedIn profile URLs

### Profile Analysis
```
GET /api/v1/profiles/analyze/{profile_id}
```
Get analysis for a scraped profile.

### Market Analysis
```
GET /api/v1/market/skills-analysis
```
Get current market skill trends.

### Export Profile
```
GET /api/v1/export/profile/{profile_id}
```
Export profile data in various formats.

**Parameters:**
- `format` (string): Export format (json, csv, pdf)

## Response Format
All responses follow this structure:
```json
{
  "status": "success|error",
  "data": {},
  "message": "Optional message"
}
```

## Error Codes
- 400: Bad Request
- 404: Not Found
- 429: Rate Limit Exceeded
- 500: Internal Server Error
""")
    
    print("✅ Documentation generated in docs/")
    return True


def check_dependencies():
    """Check if all dependencies are properly installed"""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'requests',
        'beautifulsoup4',
        'sqlalchemy',
        'pydantic'
    ]
    
    optional_modules = [
        'selenium',
        'pandas',
        'pytest',
        'black',
        'flake8'
    ]
    
    missing_required = []
    missing_optional = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing_required.append(module)
            print(f"  ❌ {module} (required)")
    
    for module in optional_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing_optional.append(module)
            print(f"  ⚠️  {module} (optional)")
    
    if missing_required:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_required)}")
        print("Run: python manage.py install")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing optional dependencies: {', '.join(missing_optional)}")
        print("These are not required but provide additional functionality")
    
    print("\n✅ All required dependencies are installed")
    return True


def show_status():
    """Show project status"""
    print("📊 LinkedIn Analyzer Agent Status")
    print("=" * 50)
    
    # Check virtual environment
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        print(f"✅ Virtual Environment: {venv}")
    else:
        print("❌ Virtual Environment: Not activated")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Environment: .env file exists")
    else:
        print("❌ Environment: .env file missing")
    
    # Check dependencies
    check_dependencies()
    
    # Check directories
    required_dirs = ["logs", "data", "temp"]
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ Directory: {dir_name}/")
        else:
            print(f"❌ Directory: {dir_name}/ missing")
    
    # Show recent logs
    log_file = Path("logs/app.log")
    if log_file.exists():
        print(f"\n📋 Recent log entries:")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:  # Last 5 lines
                print(f"  {line.strip()}")
    
    return True


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description="LinkedIn Analyzer Agent Development Tools")
    parser.add_argument("command", choices=[
        "setup", "run", "test", "lint", "format", "clean", 
        "install", "docs", "status", "deps"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    print(f"🚀 LinkedIn Analyzer Agent - {args.command.title()}")
    print("=" * 50)
    
    success = False
    
    if args.command == "setup":
        success = setup_environment()
    elif args.command == "run":
        success = run_server()
    elif args.command == "test":
        success = run_tests()
    elif args.command == "lint":
        success = lint_code()
    elif args.command == "format":
        success = format_code()
    elif args.command == "clean":
        success = clean_project()
    elif args.command == "install":
        success = install_deps()
    elif args.command == "docs":
        success = generate_docs()
    elif args.command == "status":
        success = show_status()
    elif args.command == "deps":
        success = check_dependencies()
    
    print("\n" + "=" * 50)
    if success:
        print(f"✅ {args.command.title()} completed successfully!")
    else:
        print(f"❌ {args.command.title()} failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
