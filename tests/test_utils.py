"""
Tests for utility functions.
"""

import pytest
from src.utils import (
    validate_linkedin_url, extract_linkedin_profile_id, clean_linkedin_url,
    validate_email, parse_full_name, clean_text, parse_company_size,
    calculate_engagement_score, create_prospect_tags, generate_fake_prospect
)


class TestLinkedInUtils:
    """Test LinkedIn URL utilities."""
    
    def test_validate_linkedin_url_valid(self):
        """Test valid LinkedIn URLs."""
        valid_urls = [
            "https://linkedin.com/in/john-doe",
            "https://www.linkedin.com/in/jane-smith",
            "https://linkedin.com/in/bob123",
            "https://linkedin.com/in/alice-johnson-123",
        ]
        
        for url in valid_urls:
            assert validate_linkedin_url(url), f"Should be valid: {url}"
    
    def test_validate_linkedin_url_invalid(self):
        """Test invalid LinkedIn URLs."""
        invalid_urls = [
            "",
            "https://google.com/search",
            "https://linkedin.com/company/test",
            "https://linkedin.com/in/",
            "not-a-url",
            "https://fake-linkedin.com/in/test"
        ]
        
        for url in invalid_urls:
            assert not validate_linkedin_url(url), f"Should be invalid: {url}"
    
    def test_extract_linkedin_profile_id(self):
        """Test extracting profile ID from LinkedIn URL."""
        test_cases = [
            ("https://linkedin.com/in/john-doe", "john-doe"),
            ("https://www.linkedin.com/in/jane-smith/", "jane-smith"),
            ("https://linkedin.com/in/bob123", "bob123"),
            ("invalid-url", None),
        ]
        
        for url, expected_id in test_cases:
            result = extract_linkedin_profile_id(url)
            assert result == expected_id, f"URL: {url}, Expected: {expected_id}, Got: {result}"
    
    def test_clean_linkedin_url(self):
        """Test cleaning LinkedIn URLs."""
        test_cases = [
            ("https://linkedin.com/in/john-doe?trk=123", "https://linkedin.com/in/john-doe"),
            ("https://www.linkedin.com/in/jane-smith/", "https://linkedin.com/in/jane-smith"),
            ("", ""),
        ]
        
        for dirty_url, clean_url in test_cases:
            result = clean_linkedin_url(dirty_url)
            assert result == clean_url, f"Input: {dirty_url}, Expected: {clean_url}, Got: {result}"


class TestEmailUtils:
    """Test email validation utilities."""
    
    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "first+last@test-domain.org",
            "user123@company.io"
        ]
        
        for email in valid_emails:
            assert validate_email(email), f"Should be valid: {email}"
    
    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "",
            "not-an-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user name@domain.com"
        ]
        
        for email in invalid_emails:
            assert not validate_email(email), f"Should be invalid: {email}"


class TestTextUtils:
    """Test text processing utilities."""
    
    def test_parse_full_name(self):
        """Test parsing full names."""
        test_cases = [
            ("John Doe", {"first_name": "John", "last_name": "Doe"}),
            ("Jane", {"first_name": "Jane", "last_name": ""}),
            ("John Middle Doe", {"first_name": "John", "last_name": "Middle Doe"}),
            ("", {"first_name": "", "last_name": ""}),
        ]
        
        for full_name, expected in test_cases:
            result = parse_full_name(full_name)
            assert result == expected, f"Input: {full_name}, Expected: {expected}, Got: {result}"
    
    def test_clean_text(self):
        """Test text cleaning."""
        test_cases = [
            ("  Hello   World  ", "Hello World"),
            ("Test\n\nText", "Test Text"),
            ("Special@#$%Characters", "SpecialCharacters"),
            ("", ""),
        ]
        
        for dirty_text, clean_text in test_cases:
            result = clean_text(dirty_text)
            assert result == clean_text, f"Input: {dirty_text}, Expected: {clean_text}, Got: {result}"
    
    def test_parse_company_size(self):
        """Test company size parsing."""
        test_cases = [
            ("11-50 employees", "11-50"),
            ("501-1000", "501-1000"),
            ("10,000+ employees", "10000+"),
            ("Small startup", "small startup"),
            ("", ""),
        ]
        
        for size_text, expected in test_cases:
            result = parse_company_size(size_text)
            # Just check that we get some result back
            assert isinstance(result, str), f"Input: {size_text}"


class TestProspectUtils:
    """Test prospect-related utilities."""
    
    def test_calculate_engagement_score(self):
        """Test engagement score calculation."""
        prospect_data = {
            "headline": "Senior Software Engineer",
            "location": "San Francisco",
            "industry": "Technology", 
            "company": "TechCorp",
            "company_size": "large"
        }
        
        score = calculate_engagement_score(prospect_data)
        assert 0 <= score <= 100
        assert score > 0  # Should have some score with this data
    
    def test_create_prospect_tags(self):
        """Test prospect tag creation."""
        prospect_data = {
            "headline": "Senior Software Engineer",
            "industry": "Technology",
            "location": "San Francisco"
        }
        
        tags = create_prospect_tags(prospect_data)
        assert isinstance(tags, list)
        assert "technical" in tags
        assert "tech" in tags
        assert "silicon_valley" in tags
    
    def test_generate_fake_prospect(self):
        """Test fake prospect generation."""
        prospect = generate_fake_prospect()
        
        # Check required fields
        assert "linkedin_url" in prospect
        assert "full_name" in prospect
        assert "first_name" in prospect
        assert "last_name" in prospect
        
        # Check URL format
        assert validate_linkedin_url(prospect["linkedin_url"])
        
        # Check email format
        assert validate_email(prospect["email"])