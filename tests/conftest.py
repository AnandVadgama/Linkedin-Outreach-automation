"""
Test configuration for LinkedIn Outreach Automation.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base

# Test database
TEST_DATABASE_URL = "sqlite:///test.db"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_db_session(test_engine):
    """Create test database session."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_prospect_data():
    """Sample prospect data for testing."""
    return {
        "linkedin_url": "https://linkedin.com/in/john-doe",
        "full_name": "John Doe",
        "first_name": "John",
        "last_name": "Doe",
        "headline": "Senior Software Engineer",
        "location": "San Francisco, CA",
        "industry": "Technology",
        "company": "TechCorp",
        "source": "testing"
    }