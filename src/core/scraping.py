"""
Core scraping engine for LinkedIn Analyzer Agent
"""

import asyncio
import logging
import random
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..config import settings
from ..models.profile import ProfileData

logger = logging.getLogger(__name__)


class ScrapingEngine:
    """Advanced web scraping engine with multiple strategies"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.selenium_driver: Optional[webdriver.Chrome] = None
        self.request_count = 0
        self.last_request_time = 0
    
    def _setup_selenium(self) -> webdriver.Chrome:
        """Setup Selenium WebDriver with stealth options"""
        if self.selenium_driver:
            return self.selenium_driver
        
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={settings.USER_AGENT}')
        
        # Anti-detection measures
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return self.selenium_driver
        except Exception as e:
            logger.error(f"Failed to setup Selenium driver: {e}")
            raise
    
    def _respect_rate_limit(self):
        """Implement rate limiting to be respectful"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Random delay between requests
        min_delay = settings.REQUEST_DELAY_MIN
        max_delay = settings.REQUEST_DELAY_MAX
        required_delay = random.uniform(min_delay, max_delay)
        
        if time_since_last < required_delay:
            sleep_time = required_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def check_robots_txt(self, url: str, user_agent: str = '*') -> bool:
        """Check if scraping is allowed by robots.txt"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            return rp.can_fetch(user_agent, url)
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {url}: {e}")
            return True  # Assume allowed if can't check
    
    async def scrape_with_requests(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape using requests and BeautifulSoup"""
        try:
            # Check robots.txt
            if not self.check_robots_txt(url):
                logger.warning(f"Robots.txt disallows scraping {url}")
                return None
            
            self._respect_rate_limit()
            
            response = self.session.get(url, timeout=settings.TIMEOUT_SECONDS)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'content': soup.get_text(strip=True),
                'html': str(soup),
                'status_code': response.status_code,
                'method': 'requests'
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url} with requests: {e}")
            return None
    
    async def scrape_with_selenium(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape using Selenium for JavaScript-heavy pages"""
        try:
            driver = self._setup_selenium()
            self._respect_rate_limit()
            
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            title = driver.title
            content = driver.find_element(By.TAG_NAME, "body").text
            html = driver.page_source
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'html': html,
                'status_code': 200,
                'method': 'selenium'
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url} with Selenium: {e}")
            return None
    
    async def smart_scrape(self, url: str, prefer_selenium: bool = False) -> Optional[Dict[str, Any]]:
        """Intelligent scraping that chooses the best method"""
        logger.info(f"Starting smart scrape of: {url}")
        
        # Try requests first (faster) unless Selenium is preferred
        if not prefer_selenium:
            result = await self.scrape_with_requests(url)
            if result and len(result['content']) > 100:  # Has substantial content
                logger.info(f"Successfully scraped {url} with requests")
                return result
        
        # Fall back to Selenium for dynamic content
        logger.info(f"Trying Selenium for {url}")
        result = await self.scrape_with_selenium(url)
        if result:
            logger.info(f"Successfully scraped {url} with Selenium")
            return result
        
        logger.error(f"Failed to scrape {url} with any method")
        return None
    
    def extract_linkedin_profile_data(self, scraped_data: Dict[str, Any]) -> Optional[ProfileData]:
        """Extract structured data from LinkedIn profile HTML"""
        if not scraped_data or not scraped_data.get('html'):
            return None
        
        try:
            soup = BeautifulSoup(scraped_data['html'], 'html.parser')
            
            # Extract basic profile information
            profile_data = ProfileData()
            
            # Name extraction
            name_selectors = [
                'h1.text-heading-xlarge',
                '.pv-text-details__left-panel h1',
                '[data-test-id="profile-name"]'
            ]
            
            for selector in name_selectors:
                name_element = soup.select_one(selector)
                if name_element:
                    profile_data.name = name_element.get_text(strip=True)
                    break
            
            # Headline extraction
            headline_selectors = [
                '.text-body-medium.break-words',
                '.pv-text-details__left-panel .text-body-medium',
                '[data-test-id="profile-headline"]'
            ]
            
            for selector in headline_selectors:
                headline_element = soup.select_one(selector)
                if headline_element:
                    profile_data.headline = headline_element.get_text(strip=True)
                    break
            
            # Location extraction
            location_selectors = [
                '.text-body-small.inline.t-black--light.break-words',
                '.pv-text-details__left-panel .text-body-small',
                '[data-test-id="profile-location"]'
            ]
            
            for selector in location_selectors:
                location_element = soup.select_one(selector)
                if location_element:
                    profile_data.location = location_element.get_text(strip=True)
                    break
            
            # Experience extraction
            experience_sections = soup.select('.pv-entity__summary-info, .experience-section .pv-entity__summary-info')
            for exp in experience_sections[:5]:  # Limit to first 5 experiences
                title_elem = exp.select_one('h3')
                company_elem = exp.select_one('.pv-entity__secondary-title')
                
                if title_elem:
                    experience_item = {
                        'title': title_elem.get_text(strip=True),
                        'company': company_elem.get_text(strip=True) if company_elem else '',
                        'duration': '',
                        'description': ''
                    }
                    profile_data.experience.append(experience_item)
            
            # Skills extraction
            skills_elements = soup.select('.pv-skill-category-entity__name, .skill-category-entity__name')
            for skill in skills_elements[:20]:  # Limit to first 20 skills
                skill_text = skill.get_text(strip=True)
                if skill_text:
                    profile_data.skills.append(skill_text)
            
            profile_data.url = scraped_data['url']
            profile_data.raw_html = scraped_data['html']
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn profile data: {e}")
            return None
    
    async def scrape_linkedin_profile(self, profile_url: str) -> Optional[ProfileData]:
        """Complete LinkedIn profile scraping pipeline"""
        logger.info(f"Scraping LinkedIn profile: {profile_url}")
        
        # Scrape the page
        scraped_data = await self.smart_scrape(profile_url, prefer_selenium=True)
        if not scraped_data:
            return None
        
        # Extract structured data
        profile_data = self.extract_linkedin_profile_data(scraped_data)
        return profile_data
    
    def cleanup(self):
        """Clean up resources"""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
            except Exception as e:
                logger.error(f"Error closing Selenium driver: {e}")
            finally:
                self.selenium_driver = None
        
        self.session.close()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


# Global scraping engine instance
scraping_engine = ScrapingEngine()
