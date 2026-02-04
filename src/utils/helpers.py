"""
Utility functions for LinkedIn Outreach Automation.
Provides common helper functions and data validation.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

from faker import Faker

fake = Faker()


def validate_linkedin_url(url: str) -> bool:
    """Validate if a URL is a valid LinkedIn profile URL."""
    if not url:
        return False
    
    parsed = urlparse(url)
    
    # Check if it's a LinkedIn domain
    valid_domains = ["linkedin.com", "www.linkedin.com"]
    if parsed.netloc not in valid_domains:
        return False
    
    # Check if it's a profile URL
    profile_pattern = r"^/in/[a-zA-Z0-9\-]+/?$"
    return bool(re.match(profile_pattern, parsed.path))


def extract_linkedin_profile_id(url: str) -> Optional[str]:
    """Extract the profile ID from a LinkedIn URL."""
    if not validate_linkedin_url(url):
        return None
    
    parsed = urlparse(url)
    # Extract everything after /in/
    match = re.match(r"^/in/([a-zA-Z0-9\-]+)/?$", parsed.path)
    return match.group(1) if match else None


def clean_linkedin_url(url: str) -> str:
    """Clean and normalize a LinkedIn URL."""
    if not url:
        return ""
    
    # Remove query parameters and fragments
    parsed = urlparse(url)
    clean_url = f"https://linkedin.com{parsed.path}"
    
    # Remove trailing slash
    return clean_url.rstrip("/")


def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email:
        return False
    
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


def parse_full_name(full_name: str) -> Dict[str, str]:
    """Parse full name into first and last name components."""
    if not full_name:
        return {"first_name": "", "last_name": ""}
    
    parts = full_name.strip().split()
    if len(parts) == 1:
        return {"first_name": parts[0], "last_name": ""}
    else:
        return {
            "first_name": parts[0],
            "last_name": " ".join(parts[1:])
        }


def clean_text(text: str) -> str:
    """Clean and normalize text data."""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = re.sub(r"\s+", " ", text.strip())
    
    # Remove special characters that might cause issues
    cleaned = re.sub(r"[^\w\s\-.,!?()@]", "", cleaned)
    
    return cleaned


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    if not dt:
        return ""
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_company_size(size_text: str) -> str:
    """Parse and normalize company size text."""
    if not size_text:
        return ""
    
    size_mappings = {
        "1-10": "startup",
        "11-50": "small",
        "51-200": "medium",
        "201-500": "medium-large",
        "501-1000": "large",
        "1001-5000": "large",
        "5001-10000": "enterprise",
        "10000+": "enterprise"
    }
    
    # Look for number patterns
    numbers = re.findall(r"\d+", size_text)
    if len(numbers) >= 2:
        return f"{numbers[0]}-{numbers[1]}"
    elif len(numbers) == 1:
        num = int(numbers[0])
        if num <= 10:
            return "1-10"
        elif num <= 50:
            return "11-50"
        elif num <= 200:
            return "51-200"
        elif num <= 500:
            return "201-500"
        elif num <= 1000:
            return "501-1000"
        elif num <= 5000:
            return "1001-5000"
        elif num <= 10000:
            return "5001-10000"
        else:
            return "10000+"
    
    # Return cleaned text if no numbers found
    return clean_text(size_text.lower())


def generate_connection_message_variations() -> List[str]:
    """Generate various connection message templates."""
    templates = [
        "Hi {first_name}, I'd love to connect with you to expand my professional network. Thanks!",
        "Hello {first_name}, I came across your profile and would like to connect. Looking forward to networking!",
        "Hi {first_name}, I'd like to add you to my professional network. Best regards!",
        "Hello {first_name}, I'm interested in connecting with professionals in {industry}. Would love to network!",
        "Hi {first_name}, I noticed we share similar professional interests. Would you like to connect?",
    ]
    return templates


def generate_follow_up_message_variations() -> List[str]:
    """Generate various follow-up message templates."""
    templates = [
        "Hi {first_name}, thanks for connecting! I'd love to learn more about your work at {company}.",
        "Hello {first_name}, great to connect! I'm always interested in connecting with {industry} professionals.",
        "Hi {first_name}, thanks for accepting my connection request. How are things going at {company}?",
        "Hello {first_name}, nice to connect! I'd be interested in hearing about your experience in {industry}.",
        "Hi {first_name}, thanks for connecting! Always great to network with professionals in {location}.",
    ]
    return templates


def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
    """Mask sensitive data for logging."""
    if not data:
        return ""
    
    if len(data) <= 4:
        return mask_char * len(data)
    
    # Show first 2 and last 2 characters
    return data[:2] + mask_char * (len(data) - 4) + data[-2:]


def calculate_engagement_score(prospect_data: Dict) -> float:
    """Calculate engagement score based on prospect data."""
    score = 0.0
    
    # Profile completeness
    if prospect_data.get("headline"):
        score += 10
    if prospect_data.get("location"):
        score += 10
    if prospect_data.get("industry"):
        score += 10
    if prospect_data.get("company"):
        score += 15
    
    # Profile quality indicators
    headline = prospect_data.get("headline", "").lower()
    if any(keyword in headline for keyword in ["ceo", "founder", "director", "manager"]):
        score += 20
    
    if any(keyword in headline for keyword in ["lead", "senior", "principal", "head"]):
        score += 15
    
    # Company size (larger companies might be better prospects)
    company_size = prospect_data.get("company_size", "")
    if "large" in company_size or "enterprise" in company_size:
        score += 15
    elif "medium" in company_size:
        score += 10
    
    return min(score, 100.0)  # Cap at 100


def create_prospect_tags(prospect_data: Dict) -> List[str]:
    """Create relevant tags for a prospect based on their data."""
    tags = []
    
    # Role-based tags
    headline = prospect_data.get("headline", "").lower()
    if any(keyword in headline for keyword in ["ceo", "founder"]):
        tags.append("decision_maker")
    if any(keyword in headline for keyword in ["sales", "business development"]):
        tags.append("sales")
    if any(keyword in headline for keyword in ["marketing", "growth"]):
        tags.append("marketing")
    if any(keyword in headline for keyword in ["engineer", "developer", "technical"]):
        tags.append("technical")
    if any(keyword in headline for keyword in ["hr", "people", "talent"]):
        tags.append("hr")
    
    # Industry tags
    industry = prospect_data.get("industry", "").lower()
    if "technology" in industry or "software" in industry:
        tags.append("tech")
    if "finance" in industry or "banking" in industry:
        tags.append("finance")
    if "healthcare" in industry or "medical" in industry:
        tags.append("healthcare")
    
    # Location tags
    location = prospect_data.get("location", "").lower()
    if any(city in location for city in ["san francisco", "silicon valley", "palo alto"]):
        tags.append("silicon_valley")
    if any(city in location for city in ["new york", "nyc"]):
        tags.append("new_york")
    if any(city in location for city in ["london"]):
        tags.append("london")
    
    return tags


# Test data generators for development
def generate_fake_prospect() -> Dict:
    """Generate fake prospect data for testing."""
    first_name = fake.first_name()
    last_name = fake.last_name()
    full_name = f"{first_name} {last_name}"
    
    return {
        "linkedin_url": f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
        "full_name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "headline": fake.job(),
        "location": f"{fake.city()}, {fake.state()}",
        "industry": fake.random_element(elements=[
            "Technology", "Finance", "Healthcare", "Marketing", "Sales",
            "Consulting", "Education", "Manufacturing", "Retail"
        ]),
        "company": fake.company(),
        "company_size": fake.random_element(elements=[
            "1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5000+"
        ]),
        "email": fake.email(),
        "source": "testing"
    }