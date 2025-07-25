# 🚀 LinkedIn Analyzer Agent - Quick Start Guide

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Chrome or Chromium browser
- Git (for version control)

### Automated Setup
```bash
# Clone or navigate to the project directory
cd "linkedin analyzer"

# Run the automated setup script
python setup.py
```

### Manual Setup
If you prefer manual setup:

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file with your configurations
   ```

4. **Create Directories**
   ```bash
   mkdir -p logs data temp data/exports
   ```

## Quick Start

### 1. Start the Application
```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start the server
python app.py
```

### 2. Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

### 3. Basic Usage Examples

#### Scrape a LinkedIn Profile
```bash
curl -X POST "http://localhost:8000/api/v1/profiles/scrape" \
     -H "Content-Type: application/json" \
     -d '{"profile_url": "https://www.linkedin.com/in/example-profile/"}'
```

#### Batch Scrape Multiple Profiles
```bash
curl -X POST "http://localhost:8000/api/v1/profiles/batch-scrape" \
     -H "Content-Type: application/json" \
     -d '{
       "profile_urls": [
         "https://www.linkedin.com/in/profile1/",
         "https://www.linkedin.com/in/profile2/"
       ]
     }'
```

#### Get Market Analysis
```bash
curl "http://localhost:8000/api/v1/market/skills-analysis"
```

## Project Structure
```
linkedin analyzer/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── setup.py              # Automated setup script
├── .env.example          # Environment configuration template
├── .env                  # Your environment configuration
├── README.md             # Project documentation
├── src/                  # Source code
│   ├── __init__.py
│   ├── config.py         # Application configuration
│   ├── database.py       # Database setup
│   ├── middleware.py     # Custom middleware
│   ├── utils.py          # Utility functions
│   ├── api/              # API routes
│   ├── core/             # Core functionality
│   │   ├── scraping.py   # Web scraping engine
│   │   └── logger.py     # Logging configuration
│   ├── models/           # Data models
│   │   └── profile.py    # Profile data structures
│   └── services/         # Business logic
│       ├── analyzer.py   # Profile analysis
│       └── export.py     # Data export
├── logs/                 # Application logs
├── data/                 # Data storage
│   └── exports/          # Exported files
└── temp/                 # Temporary files
```

## Key Features

### 🔍 **Web Scraping**
- Ethical LinkedIn profile scraping
- Multiple scraping strategies (requests + Selenium)
- Rate limiting and anti-detection measures
- Respects robots.txt

### 🧠 **AI Analysis**
- Profile completeness scoring
- Skill relevance analysis
- Career level detection
- Market competitiveness assessment

### 📊 **Data Export**
- JSON, CSV, Excel formats
- HTML profile reports
- Batch export capabilities

### 🚀 **API**
- RESTful API design
- Interactive documentation
- Rate limiting
- Background processing

## Configuration

### Environment Variables (.env)
```bash
# Application
DEBUG=True
HOST=127.0.0.1
PORT=8000

# Database
DATABASE_URL=sqlite:///./linkedin_analyzer.db

# API Keys (get these from respective services)
OPENAI_API_KEY=your-openai-key-here
HUGGINGFACE_API_KEY=your-huggingface-key-here

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Scraping
REQUEST_DELAY_MIN=1
REQUEST_DELAY_MAX=3
MAX_RETRIES=3
```

## Troubleshooting

### Common Issues

**1. Chrome/Selenium Issues**
```bash
# Install Chrome on Ubuntu/Debian
sudo apt-get install google-chrome-stable

# Install Chrome on macOS
brew install --cask google-chrome
```

**2. Permission Errors**
```bash
# Windows: Run as Administrator
# macOS/Linux: Check file permissions
chmod +x setup.py
```

**3. Virtual Environment Issues**
```bash
# Remove and recreate
rm -rf venv
python -m venv venv
```

**4. Port Already in Use**
```bash
# Change PORT in .env file
PORT=8001
```

### Getting Help
- Check logs in `logs/app.log`
- Enable DEBUG mode in `.env`
- Review API documentation at `/api/docs`

## Next Steps

1. **Customize Configuration**
   - Edit `.env` file with your API keys
   - Adjust scraping parameters
   - Configure database settings

2. **Enhance Features**
   - Add custom analysis algorithms
   - Implement additional export formats
   - Create custom visualizations

3. **Deploy to Production**
   - Set `DEBUG=False`
   - Use PostgreSQL database
   - Configure reverse proxy (nginx)
   - Set up monitoring

4. **Academic Project Enhancement**
   - Document methodology
   - Add performance benchmarks
   - Create presentation materials
   - Prepare demonstration scenarios

## Legal & Ethical Guidelines

⚠️ **Important**: Always respect:
- LinkedIn's Terms of Service
- Rate limiting (built-in)
- User privacy
- robots.txt compliance
- Academic integrity policies

This tool is designed for educational and research purposes. Use responsibly and ethically.
