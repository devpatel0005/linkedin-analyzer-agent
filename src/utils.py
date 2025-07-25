"""
Utility functions for LinkedIn Analyzer Agent
"""

import re
import hashlib
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def validate_linkedin_url(url: str) -> bool:
    """Validate if URL is a proper LinkedIn profile URL"""
    pattern = r'^https://www\.linkedin\.com/in/[a-zA-Z0-9\-]+/?$'
    return bool(re.match(pattern, url))


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\-.,!?()]', '', text)
    
    return text


def extract_profile_id_from_url(url: str) -> Optional[str]:
    """Extract profile ID from LinkedIn URL"""
    match = re.search(r'/in/([a-zA-Z0-9\-]+)', url)
    return match.group(1) if match else None


def generate_profile_hash(profile_url: str) -> str:
    """Generate a unique hash for a profile URL"""
    return hashlib.md5(profile_url.encode()).hexdigest()


def normalize_skill_name(skill: str) -> str:
    """Normalize skill names for consistency"""
    # Convert to title case and remove extra spaces
    normalized = ' '.join(word.capitalize() for word in skill.strip().split())
    
    # Handle common abbreviations
    abbreviations = {
        'Ai': 'AI',
        'Ml': 'ML',
        'Api': 'API',
        'Ui': 'UI',
        'Ux': 'UX',
        'Seo': 'SEO',
        'Aws': 'AWS',
        'Gcp': 'GCP',
        'Sql': 'SQL',
        'Html': 'HTML',
        'Css': 'CSS',
        'Javascript': 'JavaScript',
        'Nodejs': 'Node.js',
        'Reactjs': 'React.js'
    }
    
    for old, new in abbreviations.items():
        normalized = normalized.replace(old, new)
    
    return normalized


def parse_duration_string(duration: str) -> Dict[str, Any]:
    """Parse duration strings like '2 yrs 3 mos' into structured data"""
    if not duration:
        return {'years': 0, 'months': 0, 'total_months': 0}
    
    years = 0
    months = 0
    
    # Extract years
    year_match = re.search(r'(\d+)\s*(?:yr|year)', duration, re.IGNORECASE)
    if year_match:
        years = int(year_match.group(1))
    
    # Extract months
    month_match = re.search(r'(\d+)\s*(?:mo|month)', duration, re.IGNORECASE)
    if month_match:
        months = int(month_match.group(1))
    
    total_months = years * 12 + months
    
    return {
        'years': years,
        'months': months,
        'total_months': total_months
    }


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity using Jaccard similarity"""
    if not text1 or not text2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def extract_years_from_date_range(start_date: str, end_date: str = None) -> float:
    """Extract years from date range"""
    try:
        # Parse start date
        start = datetime.strptime(start_date, '%Y-%m-%d') if isinstance(start_date, str) else start_date
        
        # Use current date if end_date is None or "Present"
        if not end_date or end_date.lower() in ['present', 'current', 'now']:
            end = datetime.now()
        else:
            end = datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
        
        # Calculate difference in years
        years = (end - start).days / 365.25
        return max(0, years)
        
    except (ValueError, AttributeError):
        return 0.0


def format_number(number: int) -> str:
    """Format large numbers with K/M suffixes"""
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)


def detect_programming_languages(text: str) -> List[str]:
    """Detect programming languages mentioned in text"""
    languages = [
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'C', 'PHP', 'Ruby',
        'Go', 'Rust', 'Swift', 'Kotlin', 'TypeScript', 'Scala', 'R',
        'MATLAB', 'SQL', 'HTML', 'CSS', 'Shell', 'PowerShell'
    ]
    
    found_languages = []
    text_lower = text.lower()
    
    for lang in languages:
        if lang.lower() in text_lower:
            found_languages.append(lang)
    
    return found_languages


def extract_email_from_text(text: str) -> Optional[str]:
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group() if match else None


def extract_phone_from_text(text: str) -> Optional[str]:
    """Extract phone number from text"""
    phone_patterns = [
        r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
        r'\+?([0-9]{1,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})'
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    
    return None


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)]
    return truncated + suffix


def batch_process(items: List[Any], batch_size: int = 10):
    """Process items in batches"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with nested key support"""
    try:
        keys = key.split('.')
        value = dictionary
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default


def rate_limit_delay(request_count: int, max_requests_per_minute: int = 60) -> float:
    """Calculate delay needed for rate limiting"""
    if request_count >= max_requests_per_minute:
        return 60.0  # Wait full minute if limit exceeded
    
    # Calculate proportional delay
    delay = (60.0 / max_requests_per_minute) * request_count
    return min(delay, 60.0)


class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str = "operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        print(f"{self.operation_name} completed in {duration:.3f} seconds")
    
    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
