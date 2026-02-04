"""
LinkedIn service for web automation and data scraping.
Handles LinkedIn login, prospect search, and connection automation.
"""

import random
import time
from datetime import datetime
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from ..core.config import settings
from ..core.exceptions import (
    AuthenticationError, AutomationError, NetworkError, RateLimitError
)
from ..core.logging import LoggerMixin


class LinkedInService(LoggerMixin):
    """LinkedIn automation service using Selenium."""
    
    def __init__(self):
        super().__init__()
        self.driver: Optional[webdriver.Chrome] = None
        self.is_authenticated = False
        self.daily_actions_count = {"connections": 0, "messages": 0}
        
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options."""
        try:
            options = Options()
            
            if settings.headless_browser:
                options.add_argument("--headless")
            
            # Essential options for LinkedIn
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Install and setup ChromeDriver
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=options
            )
            
            # Remove navigator.webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.log_action("WebDriver setup completed")
            return driver
            
        except Exception as e:
            raise NetworkError(f"Failed to setup WebDriver: {str(e)}")
    
    def login(self, email: str = None, password: str = None) -> bool:
        """Login to LinkedIn."""
        try:
            email = email or settings.linkedin_email
            password = password or settings.linkedin_password
            
            if not email or not password:
                raise AuthenticationError("LinkedIn credentials not provided")
            
            self.driver = self._setup_driver()
            
            self.log_action("Starting LinkedIn login", email=email)
            
            # Navigate to LinkedIn login
            self.driver.get("https://www.linkedin.com/login")
            self._random_delay(2, 4)
            
            # Find and fill email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            self._type_like_human(email_field, email)
            
            # Find and fill password
            password_field = self.driver.find_element(By.ID, "password")
            self._type_like_human(password_field, password)
            
            # Click sign in
            signin_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            signin_button.click()
            
            # Wait for successful login or handle 2FA/captcha
            self._random_delay(3, 5)
            
            # Check if we're logged in
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
                )
                self.is_authenticated = True
                self.log_success("LinkedIn login successful")
                return True
                
            except TimeoutException:
                # Check for security challenges
                if "challenge" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                    self.log_error("LinkedIn security challenge detected - manual intervention required")
                    raise AuthenticationError("Security challenge detected - please complete manually")
                else:
                    raise AuthenticationError("Login failed - check credentials")
                    
        except Exception as e:
            self.log_error("LinkedIn login failed", error=str(e))
            if isinstance(e, (AuthenticationError, AutomationError)):
                raise
            raise AuthenticationError(f"Login failed: {str(e)}")
    
    def search_prospects(self, keywords: str, location: str = None, limit: int = 25) -> List[Dict]:
        """Search for prospects on LinkedIn."""
        if not self.is_authenticated:
            raise AuthenticationError("Must be logged in to search prospects")
        
        try:
            self.log_action("Searching prospects", keywords=keywords, location=location, limit=limit)
            
            # Build search URL
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}"
            if location:
                search_url += f"&origin=SWITCH_SEARCH_VERTICAL&geoUrn=%5B%22{location}%22%5D"
            
            self.driver.get(search_url)
            self._random_delay(3, 5)
            
            prospects = []
            
            # Scroll and collect prospects
            for page in range(0, min(limit // 10 + 1, 5)):  # LinkedIn shows ~10 results per "page"
                self._scroll_page()
                self._random_delay(2, 4)
                
                # Find prospect elements
                prospect_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "li[data-view-name='search-results-person']"
                )
                
                for element in prospect_elements:
                    if len(prospects) >= limit:
                        break
                        
                    prospect = self._extract_prospect_data(element)
                    if prospect:
                        prospects.append(prospect)
                
                if len(prospects) >= limit:
                    break
            
            self.log_success(f"Found {len(prospects)} prospects", count=len(prospects))
            return prospects
            
        except Exception as e:
            self.log_error("Prospect search failed", error=str(e))
            raise AutomationError(f"Prospect search failed: {str(e)}")
    
    def send_connection_request(self, prospect_url: str, message: str = None) -> bool:
        """Send a connection request to a prospect."""
        if not self.is_authenticated:
            raise AuthenticationError("Must be logged in to send connection requests")
        
        if self._check_daily_limits("connections"):
            raise RateLimitError("Daily connection request limit reached")
        
        try:
            self.log_action("Sending connection request", prospect_url=prospect_url)
            
            # Navigate to prospect profile
            self.driver.get(prospect_url)
            self._random_delay(3, 5)
            
            # Find connect button
            connect_button = None
            possible_selectors = [
                "button[aria-label*='Invite'][aria-label*='to connect']",
                "button[data-control-name='connect']",
                "//button[contains(text(), 'Connect')]"
            ]
            
            for selector in possible_selectors:
                try:
                    if selector.startswith("//"):
                        connect_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        connect_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not connect_button:
                self.log_error("Connect button not found")
                return False
            
            connect_button.click()
            self._random_delay(1, 3)
            
            # Handle message modal if it appears
            try:
                # Look for "Add a note" button
                add_note_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add a note')]"))
                )
                
                if message and add_note_button:
                    add_note_button.click()
                    self._random_delay(1, 2)
                    
                    # Find message textarea
                    message_field = self.driver.find_element(
                        By.CSS_SELECTOR, "textarea[name='message']"
                    )
                    self._type_like_human(message_field, message)
                    self._random_delay(1, 2)
                
                # Click Send button
                send_button = self.driver.find_element(
                    By.XPATH, "//button[contains(text(), 'Send') or contains(text(), 'Send invitation')]"
                )
                send_button.click()
                
            except TimeoutException:
                # No message modal, probably direct send
                pass
            
            self._random_delay(2, 4)
            self.daily_actions_count["connections"] += 1
            
            self.log_success("Connection request sent successfully")
            return True
            
        except Exception as e:
            self.log_error("Failed to send connection request", error=str(e))
            return False
    
    def _extract_prospect_data(self, element) -> Optional[Dict]:
        """Extract prospect data from search result element."""
        try:
            prospect = {}
            
            # Name and profile link
            name_link = element.find_element(
                By.CSS_SELECTOR, 
                "a[data-control-name='search_srp_result'] span[aria-hidden='true']"
            )
            prospect["full_name"] = name_link.text.strip()
            prospect["linkedin_url"] = name_link.find_element(By.XPATH, "../..").get_attribute("href")
            
            # Split name
            name_parts = prospect["full_name"].split()
            prospect["first_name"] = name_parts[0] if name_parts else ""
            prospect["last_name"] = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            # Headline
            try:
                headline = element.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
                prospect["headline"] = headline.text.strip()
            except NoSuchElementException:
                prospect["headline"] = ""
            
            # Location
            try:
                location = element.find_element(By.CSS_SELECTOR, ".entity-result__secondary-subtitle")
                prospect["location"] = location.text.strip()
            except NoSuchElementException:
                prospect["location"] = ""
            
            # Profile picture
            try:
                img = element.find_element(By.CSS_SELECTOR, "img[data-ghost-classes]")
                prospect["profile_picture_url"] = img.get_attribute("src")
            except NoSuchElementException:
                prospect["profile_picture_url"] = ""
            
            prospect["source"] = "linkedin_search"
            prospect["created_at"] = datetime.utcnow().isoformat()
            
            return prospect
            
        except Exception as e:
            self.log_error("Failed to extract prospect data", error=str(e))
            return None
    
    def _type_like_human(self, element, text: str):
        """Type text with human-like delays."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
    
    def _random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Add random delay between actions."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _scroll_page(self):
        """Scroll page to load more content."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self._random_delay(1, 3)
    
    def _check_daily_limits(self, action_type: str) -> bool:
        """Check if daily limits have been reached."""
        if not settings.rate_limit_enabled:
            return False
        
        limits = {
            "connections": settings.max_connection_requests_per_day,
            "messages": settings.max_messages_per_day
        }
        
        current_count = self.daily_actions_count.get(action_type, 0)
        return current_count >= limits.get(action_type, 0)
    
    def close(self):
        """Close the browser and cleanup."""
        if self.driver:
            self.driver.quit()
            self.log_action("LinkedIn service closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()