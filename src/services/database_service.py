"""
Database service for managing prospects, campaigns, and automation data.
Provides high-level database operations with proper error handling.
"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..core.exceptions import DatabaseError, ProspectNotFoundError, ValidationError
from ..core.logging import LoggerMixin
from ..models import (
    get_db, Prospect, ProspectStatus, ConnectionRequest, 
    ConnectionStatus, Message, Campaign
)


class DatabaseService(LoggerMixin):
    """Database service for LinkedIn outreach automation."""
    
    def __init__(self, db: Session = None):
        super().__init__()
        self.db = db or next(get_db())
    
    # Prospect Management
    def create_prospect(self, prospect_data: Dict) -> Prospect:
        """Create a new prospect."""
        try:
            # Check if prospect already exists
            existing = self.get_prospect_by_url(prospect_data.get("linkedin_url"))
            if existing:
                self.log_action("Prospect already exists", linkedin_url=prospect_data.get("linkedin_url"))
                return existing
            
            # Validate required fields
            required_fields = ["linkedin_url", "full_name"]
            for field in required_fields:
                if not prospect_data.get(field):
                    raise ValidationError(f"Required field missing: {field}")
            
            prospect = Prospect(**prospect_data)
            self.db.add(prospect)
            self.db.commit()
            self.db.refresh(prospect)
            
            self.log_success("Prospect created", prospect_id=prospect.id, name=prospect.full_name)
            return prospect
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.log_error("Database error creating prospect", error=str(e))
            raise DatabaseError(f"Failed to create prospect: {str(e)}")
    
    def get_prospect_by_url(self, linkedin_url: str) -> Optional[Prospect]:
        """Get prospect by LinkedIn URL."""
        try:
            return self.db.query(Prospect).filter(Prospect.linkedin_url == linkedin_url).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get prospect: {str(e)}")
    
    def get_prospect_by_id(self, prospect_id: int) -> Optional[Prospect]:
        """Get prospect by ID."""
        try:
            prospect = self.db.query(Prospect).filter(Prospect.id == prospect_id).first()
            if not prospect:
                raise ProspectNotFoundError(f"Prospect with ID {prospect_id} not found")
            return prospect
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get prospect: {str(e)}")
    
    def update_prospect_status(self, prospect_id: int, status: ProspectStatus) -> Prospect:
        """Update prospect status."""
        try:
            prospect = self.get_prospect_by_id(prospect_id)
            prospect.status = status
            prospect.updated_at = datetime.utcnow()
            
            if status in [ProspectStatus.CONTACTED, ProspectStatus.CONNECTED]:
                prospect.last_contacted_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(prospect)
            
            self.log_success("Prospect status updated", 
                           prospect_id=prospect_id, 
                           status=status.value)
            return prospect
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update prospect status: {str(e)}")
    
    def get_prospects_by_status(self, status: ProspectStatus, limit: int = None) -> List[Prospect]:
        """Get prospects by status."""
        try:
            query = self.db.query(Prospect).filter(Prospect.status == status)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get prospects by status: {str(e)}")
    
    def search_prospects(self, **filters) -> List[Prospect]:
        """Search prospects with filters."""
        try:
            query = self.db.query(Prospect)
            
            # Apply filters
            if filters.get("status"):
                query = query.filter(Prospect.status == filters["status"])
            if filters.get("company"):
                query = query.filter(Prospect.company.ilike(f"%{filters['company']}%"))
            if filters.get("location"):
                query = query.filter(Prospect.location.ilike(f"%{filters['location']}%"))
            if filters.get("industry"):
                query = query.filter(Prospect.industry.ilike(f"%{filters['industry']}%"))
            
            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to search prospects: {str(e)}")
    
    # Connection Request Management
    def create_connection_request(self, prospect_id: int, message: str = None) -> ConnectionRequest:
        """Create a connection request record."""
        try:
            # Check if connection request already exists
            existing = self.db.query(ConnectionRequest).filter(
                ConnectionRequest.prospect_id == prospect_id
            ).first()
            
            if existing:
                self.log_action("Connection request already exists", prospect_id=prospect_id)
                return existing
            
            connection_request = ConnectionRequest(
                prospect_id=prospect_id,
                message=message,
                status=ConnectionStatus.PENDING
            )
            
            self.db.add(connection_request)
            self.db.commit()
            self.db.refresh(connection_request)
            
            # Update prospect status
            self.update_prospect_status(prospect_id, ProspectStatus.CONTACTED)
            
            self.log_success("Connection request created", 
                           prospect_id=prospect_id,
                           request_id=connection_request.id)
            return connection_request
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create connection request: {str(e)}")
    
    def update_connection_status(self, request_id: int, status: ConnectionStatus) -> ConnectionRequest:
        """Update connection request status."""
        try:
            request = self.db.query(ConnectionRequest).filter(
                ConnectionRequest.id == request_id
            ).first()
            
            if not request:
                raise DatabaseError(f"Connection request {request_id} not found")
            
            request.status = status
            request.response_at = datetime.utcnow()
            
            # Update prospect status if connected
            if status == ConnectionStatus.ACCEPTED:
                self.update_prospect_status(request.prospect_id, ProspectStatus.CONNECTED)
            
            self.db.commit()
            self.db.refresh(request)
            
            self.log_success("Connection status updated", 
                           request_id=request_id,
                           status=status.value)
            return request
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update connection status: {str(e)}")
    
    def get_pending_connections(self, limit: int = None) -> List[ConnectionRequest]:
        """Get pending connection requests."""
        try:
            query = self.db.query(ConnectionRequest).filter(
                ConnectionRequest.status == ConnectionStatus.PENDING
            )
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get pending connections: {str(e)}")
    
    # Message Management
    def create_message(self, prospect_id: int, content: str, 
                      is_sent_by_us: bool = True, message_type: str = "outreach") -> Message:
        """Create a message record."""
        try:
            message = Message(
                prospect_id=prospect_id,
                content=content,
                is_sent_by_us=is_sent_by_us,
                message_type=message_type
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            self.log_success("Message created", 
                           prospect_id=prospect_id,
                           message_id=message.id,
                           type=message_type)
            return message
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create message: {str(e)}")
    
    def get_conversation(self, prospect_id: int) -> List[Message]:
        """Get all messages for a prospect."""
        try:
            return self.db.query(Message).filter(
                Message.prospect_id == prospect_id
            ).order_by(Message.sent_at).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get conversation: {str(e)}")
    
    # Campaign Management
    def create_campaign(self, campaign_data: Dict) -> Campaign:
        """Create a new campaign."""
        try:
            campaign = Campaign(**campaign_data)
            self.db.add(campaign)
            self.db.commit()
            self.db.refresh(campaign)
            
            self.log_success("Campaign created", 
                           campaign_id=campaign.id,
                           name=campaign.name)
            return campaign
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create campaign: {str(e)}")
    
    def get_active_campaigns(self) -> List[Campaign]:
        """Get all active campaigns."""
        try:
            return self.db.query(Campaign).filter(Campaign.is_active == True).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get active campaigns: {str(e)}")
    
    # Analytics and Reporting
    def get_prospect_stats(self) -> Dict:
        """Get prospect statistics."""
        try:
            stats = {}
            
            # Total prospects
            stats["total_prospects"] = self.db.query(Prospect).count()
            
            # Prospects by status
            for status in ProspectStatus:
                count = self.db.query(Prospect).filter(Prospect.status == status).count()
                stats[f"prospects_{status.value}"] = count
            
            # Connection requests
            stats["total_connection_requests"] = self.db.query(ConnectionRequest).count()
            stats["pending_connections"] = self.db.query(ConnectionRequest).filter(
                ConnectionRequest.status == ConnectionStatus.PENDING
            ).count()
            stats["accepted_connections"] = self.db.query(ConnectionRequest).filter(
                ConnectionRequest.status == ConnectionStatus.ACCEPTED
            ).count()
            
            # Messages
            stats["total_messages"] = self.db.query(Message).count()
            stats["sent_messages"] = self.db.query(Message).filter(
                Message.is_sent_by_us == True
            ).count()
            stats["received_messages"] = self.db.query(Message).filter(
                Message.is_sent_by_us == False
            ).count()
            
            return stats
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get prospect stats: {str(e)}")
    
    def close(self):
        """Close database session."""
        if self.db:
            self.db.close()