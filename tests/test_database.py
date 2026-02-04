"""
Tests for database models and operations.
"""

import pytest
from datetime import datetime

from src.models import Prospect, ProspectStatus, ConnectionRequest, ConnectionStatus
from src.services import DatabaseService


class TestProspectModel:
    """Test Prospect model."""
    
    def test_create_prospect(self, test_db_session, sample_prospect_data):
        """Test creating a prospect."""
        prospect = Prospect(**sample_prospect_data)
        test_db_session.add(prospect)
        test_db_session.commit()
        
        assert prospect.id is not None
        assert prospect.full_name == "John Doe"
        assert prospect.status == ProspectStatus.NEW
        assert prospect.created_at is not None
    
    def test_prospect_repr(self, test_db_session, sample_prospect_data):
        """Test prospect string representation."""
        prospect = Prospect(**sample_prospect_data)
        test_db_session.add(prospect)
        test_db_session.commit()
        
        repr_str = repr(prospect)
        assert "John Doe" in repr_str
        assert "new" in repr_str


class TestDatabaseService:
    """Test DatabaseService operations."""
    
    def test_create_prospect(self, test_db_session, sample_prospect_data):
        """Test creating prospect through service."""
        db_service = DatabaseService(test_db_session)
        
        prospect = db_service.create_prospect(sample_prospect_data)
        
        assert prospect.id is not None
        assert prospect.full_name == "John Doe"
        assert prospect.linkedin_url == "https://linkedin.com/in/john-doe"
    
    def test_create_duplicate_prospect(self, test_db_session, sample_prospect_data):
        """Test creating duplicate prospect returns existing one."""
        db_service = DatabaseService(test_db_session)
        
        # Create first prospect
        prospect1 = db_service.create_prospect(sample_prospect_data)
        
        # Try to create duplicate
        prospect2 = db_service.create_prospect(sample_prospect_data)
        
        assert prospect1.id == prospect2.id
    
    def test_get_prospect_by_url(self, test_db_session, sample_prospect_data):
        """Test getting prospect by LinkedIn URL."""
        db_service = DatabaseService(test_db_session)
        
        # Create prospect
        created_prospect = db_service.create_prospect(sample_prospect_data)
        
        # Retrieve by URL
        found_prospect = db_service.get_prospect_by_url(sample_prospect_data["linkedin_url"])
        
        assert found_prospect.id == created_prospect.id
        assert found_prospect.full_name == "John Doe"
    
    def test_update_prospect_status(self, test_db_session, sample_prospect_data):
        """Test updating prospect status."""
        db_service = DatabaseService(test_db_session)
        
        prospect = db_service.create_prospect(sample_prospect_data)
        original_updated_at = prospect.updated_at
        
        # Update status
        updated_prospect = db_service.update_prospect_status(prospect.id, ProspectStatus.CONTACTED)
        
        assert updated_prospect.status == ProspectStatus.CONTACTED
        assert updated_prospect.last_contacted_at is not None
        assert updated_prospect.updated_at != original_updated_at
    
    def test_create_connection_request(self, test_db_session, sample_prospect_data):
        """Test creating connection request."""
        db_service = DatabaseService(test_db_session)
        
        prospect = db_service.create_prospect(sample_prospect_data)
        
        connection_request = db_service.create_connection_request(
            prospect.id, 
            "Hi John, would love to connect!"
        )
        
        assert connection_request.prospect_id == prospect.id
        assert connection_request.message == "Hi John, would love to connect!"
        assert connection_request.status == ConnectionStatus.PENDING
        
        # Check that prospect status was updated
        updated_prospect = db_service.get_prospect_by_id(prospect.id)
        assert updated_prospect.status == ProspectStatus.CONTACTED
    
    def test_get_prospect_stats(self, test_db_session):
        """Test getting prospect statistics."""
        db_service = DatabaseService(test_db_session)
        
        # Create some test data
        prospect_data_1 = {
            "linkedin_url": "https://linkedin.com/in/jane-smith",
            "full_name": "Jane Smith",
            "source": "test"
        }
        
        prospect_data_2 = {
            "linkedin_url": "https://linkedin.com/in/bob-johnson", 
            "full_name": "Bob Johnson",
            "source": "test"
        }
        
        prospect1 = db_service.create_prospect(prospect_data_1)
        prospect2 = db_service.create_prospect(prospect_data_2)
        
        # Update one prospect status
        db_service.update_prospect_status(prospect1.id, ProspectStatus.CONTACTED)
        
        # Get stats
        stats = db_service.get_prospect_stats()
        
        assert stats["total_prospects"] == 2
        assert stats["prospects_new"] == 1
        assert stats["prospects_contacted"] == 1