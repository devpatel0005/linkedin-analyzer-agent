#!/usr/bin/env python3
"""
Setup script for LinkedIn Analyzer Agent
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    # Create virtual environment
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    return True

def get_pip_command():
    """Get the correct pip command for the platform"""
    system = platform.system().lower()
    if system == "windows":
        return "venv\\Scripts\\pip"
    else:
        return "venv/bin/pip"

def install_dependencies():
    """Install Python dependencies"""
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    directories = ["logs", "data", "temp", "data/exports"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def setup_environment_file():
    """Setup environment configuration"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from .env.example")
        print("📝 Please edit .env file to add your API keys and configuration")
    else:
        print("⚠️  .env.example not found, creating basic .env file")
        basic_env = """# LinkedIn Analyzer Agent Environment
DEBUG=True
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./linkedin_analyzer.db
LOG_LEVEL=INFO
SECRET_KEY=dev-secret-key-change-in-production
"""
        with open(env_file, 'w') as f:
            f.write(basic_env)
        
        print("✅ Created basic .env file")
    
    return True

def check_optional_dependencies():
    """Check for optional system dependencies"""
    print("\n🔍 Checking optional dependencies...")
    
    # Check for Chrome/Chromium (for Selenium)
    chrome_paths = [
        "google-chrome",
        "chromium",
        "chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]
    
    chrome_found = False
    for chrome_path in chrome_paths:
        try:
            if os.path.exists(chrome_path) or subprocess.run(f"which {chrome_path}", 
                                                           shell=True, 
                                                           capture_output=True).returncode == 0:
                print(f"✅ Chrome/Chromium found: {chrome_path}")
                chrome_found = True
                break
        except:
            continue
    
    if not chrome_found:
        print("⚠️  Chrome/Chromium not found. Some scraping features may not work.")
        print("   Please install Google Chrome or Chromium for full functionality.")
    
    return True

def run_tests():
    """Run basic tests to verify installation"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        import requests
        import bs4
        # import selenium  # Commented out since selenium might not be available
        print("✅ Core dependencies import successfully")
        
        # Test application import
        sys.path.insert(0, str(Path.cwd()))
        from src.config import settings
        print("✅ Application configuration loaded")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 LinkedIn Analyzer Agent Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Setup virtual environment
    if success and not setup_virtual_environment():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Setup directories
    if success and not setup_directories():
        success = False
    
    # Setup environment file
    if success and not setup_environment_file():
        success = False
    
    # Check optional dependencies
    if success:
        check_optional_dependencies()
    
    # Run tests
    if success and not run_tests():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file to add your API keys")
        print("2. Activate virtual environment:")
        
        system = platform.system().lower()
        if system == "windows":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        
        print("3. Run the application:")
        print("   python app.py")
        print("\n4. Open http://localhost:8000 in your browser")
        print("5. API documentation: http://localhost:8000/api/docs")
    else:
        print("❌ Setup failed. Please check the errors above and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
