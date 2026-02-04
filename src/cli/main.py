"""
Command-line interface for LinkedIn Outreach Automation.
Provides easy-to-use commands for managing prospects and automation.
"""

import click
from datetime import datetime
from typing import List

from ..core import settings, get_logger
from ..core.exceptions import LinkedInAutomationError
from ..models import init_database, check_database_exists, ProspectStatus
from ..services import DatabaseService, LinkedInService
from ..utils import generate_fake_prospect, validate_linkedin_url

logger = get_logger(__name__)


@click.group()
@click.version_option(version=settings.app_version)
def cli():
    """LinkedIn Outreach Automation CLI - Version 0.1.0"""
    pass


@cli.command()
def init_db():
    """Initialize the database with required tables."""
    try:
        if check_database_exists():
            click.echo("⚠️  Database already exists!")
            if click.confirm("Do you want to recreate it?"):
                init_database()
                click.echo("✅ Database recreated successfully!")
            else:
                click.echo("Database initialization cancelled.")
        else:
            init_database()
            click.echo("✅ Database initialized successfully!")
            
    except Exception as e:
        click.echo(f"❌ Failed to initialize database: {str(e)}")
        logger.error("Database initialization failed", error=str(e))


@cli.command()
@click.option("--keywords", required=True, help="Search keywords (e.g., 'software engineer')")
@click.option("--location", help="Target location (e.g., 'San Francisco')")
@click.option("--limit", default=25, help="Number of prospects to find (default: 25)")
@click.option("--save", is_flag=True, help="Save prospects to database")
def search_prospects(keywords: str, location: str, limit: int, save: bool):
    """Search for prospects on LinkedIn."""
    try:
        click.echo(f"🔍 Searching for prospects...")
        click.echo(f"Keywords: {keywords}")
        if location:
            click.echo(f"Location: {location}")
        click.echo(f"Limit: {limit}")
        click.echo()
        
        with LinkedInService() as linkedin:
            # Login
            click.echo("🔐 Logging into LinkedIn...")
            if linkedin.login():
                click.echo("✅ Login successful!")
            else:
                click.echo("❌ Login failed!")
                return
            
            # Search prospects
            click.echo("🔍 Searching prospects...")
            prospects = linkedin.search_prospects(
                keywords=keywords, 
                location=location, 
                limit=limit
            )
            
            if not prospects:
                click.echo("No prospects found.")
                return
            
            click.echo(f"✅ Found {len(prospects)} prospects!")
            
            # Display results
            for i, prospect in enumerate(prospects, 1):
                click.echo(f"\n{i}. {prospect['full_name']}")
                click.echo(f"   Headline: {prospect.get('headline', 'N/A')}")
                click.echo(f"   Location: {prospect.get('location', 'N/A')}")
                click.echo(f"   LinkedIn: {prospect['linkedin_url']}")
            
            # Save to database if requested
            if save:
                click.echo("\n💾 Saving prospects to database...")
                db_service = DatabaseService()
                saved_count = 0
                
                for prospect in prospects:
                    try:
                        db_service.create_prospect(prospect)
                        saved_count += 1
                    except Exception as e:
                        logger.error("Failed to save prospect", 
                                   prospect=prospect['full_name'], 
                                   error=str(e))
                
                click.echo(f"✅ Saved {saved_count} prospects to database!")
                db_service.close()
            
    except LinkedInAutomationError as e:
        click.echo(f"❌ {str(e)}")
        logger.error("Prospect search failed", error=str(e))
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}")
        logger.error("Unexpected error in prospect search", error=str(e))


@cli.command()
@click.option("--limit", default=10, help="Number of connection requests to send (default: 10)")
@click.option("--message", help="Personal message to include with connection requests")
@click.option("--dry-run", is_flag=True, help="Show what would be done without actually doing it")
def send_connections(limit: int, message: str, dry_run: bool):
    """Send connection requests to prospects."""
    try:
        db_service = DatabaseService()
        
        # Get prospects with NEW status
        prospects = db_service.get_prospects_by_status(
            status=ProspectStatus.NEW,
            limit=limit
        )
        
        if not prospects:
            click.echo("No new prospects found to contact.")
            return
        
        click.echo(f"📤 {'[DRY RUN] ' if dry_run else ''}Sending connection requests to {len(prospects)} prospects...")
        
        if dry_run:
            for i, prospect in enumerate(prospects, 1):
                click.echo(f"{i}. {prospect.full_name} ({prospect.company})")
            click.echo(f"\nWould send {len(prospects)} connection requests.")
            return
        
        with LinkedInService() as linkedin:
            # Login
            click.echo("🔐 Logging into LinkedIn...")
            if not linkedin.login():
                click.echo("❌ Login failed!")
                return
            
            success_count = 0
            
            for i, prospect in enumerate(prospects, 1):
                click.echo(f"\n{i}/{len(prospects)} Sending to {prospect.full_name}...")
                
                try:
                    if linkedin.send_connection_request(prospect.linkedin_url, message):
                        # Record in database
                        db_service.create_connection_request(prospect.id, message)
                        success_count += 1
                        click.echo("✅ Sent successfully!")
                    else:
                        click.echo("❌ Failed to send")
                        
                except Exception as e:
                    click.echo(f"❌ Error: {str(e)}")
                    logger.error("Connection request failed", 
                               prospect=prospect.full_name, 
                               error=str(e))
            
            click.echo(f"\n✅ Successfully sent {success_count} connection requests!")
        
        db_service.close()
        
    except LinkedInAutomationError as e:
        click.echo(f"❌ {str(e)}")
        logger.error("Send connections failed", error=str(e))
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}")
        logger.error("Unexpected error in send connections", error=str(e))


@cli.command()
def list_prospects():
    """List all prospects in the database."""
    try:
        db_service = DatabaseService()
        prospects = db_service.search_prospects()
        
        if not prospects:
            click.echo("No prospects found in database.")
            return
        
        click.echo(f"📋 Found {len(prospects)} prospects:\n")
        
        # Group by status
        by_status = {}
        for prospect in prospects:
            status = prospect.status.value
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(prospect)
        
        for status, prospect_list in by_status.items():
            click.echo(f"🏷️  {status.upper()} ({len(prospect_list)})")
            for prospect in prospect_list[:10]:  # Show first 10
                click.echo(f"   • {prospect.full_name} - {prospect.company or 'No company'}")
            if len(prospect_list) > 10:
                click.echo(f"   ... and {len(prospect_list) - 10} more")
            click.echo()
        
        db_service.close()
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        logger.error("List prospects failed", error=str(e))


@cli.command()
def stats():
    """Show automation statistics."""
    try:
        db_service = DatabaseService()
        stats = db_service.get_prospect_stats()
        
        click.echo("📊 LinkedIn Outreach Automation Stats\n")
        
        # Prospect stats
        click.echo("👥 PROSPECTS")
        click.echo(f"   Total: {stats.get('total_prospects', 0)}")
        click.echo(f"   New: {stats.get('prospects_new', 0)}")
        click.echo(f"   Contacted: {stats.get('prospects_contacted', 0)}")
        click.echo(f"   Connected: {stats.get('prospects_connected', 0)}")
        click.echo(f"   Replied: {stats.get('prospects_replied', 0)}")
        click.echo(f"   Converted: {stats.get('prospects_converted', 0)}")
        click.echo()
        
        # Connection stats
        click.echo("🤝 CONNECTIONS")
        click.echo(f"   Total Requests: {stats.get('total_connection_requests', 0)}")
        click.echo(f"   Pending: {stats.get('pending_connections', 0)}")
        click.echo(f"   Accepted: {stats.get('accepted_connections', 0)}")
        click.echo()
        
        # Message stats
        click.echo("💬 MESSAGES")
        click.echo(f"   Total: {stats.get('total_messages', 0)}")
        click.echo(f"   Sent: {stats.get('sent_messages', 0)}")
        click.echo(f"   Received: {stats.get('received_messages', 0)}")
        
        # Calculate rates
        if stats.get('total_connection_requests', 0) > 0:
            acceptance_rate = (stats.get('accepted_connections', 0) / 
                             stats.get('total_connection_requests', 1)) * 100
            click.echo(f"\n📈 Connection Acceptance Rate: {acceptance_rate:.1f}%")
        
        db_service.close()
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        logger.error("Stats failed", error=str(e))


@cli.command()
@click.option("--count", default=10, help="Number of fake prospects to generate")
def generate_test_data(count: int):
    """Generate test prospect data for development."""
    try:
        click.echo(f"🧪 Generating {count} test prospects...")
        
        db_service = DatabaseService()
        
        for i in range(count):
            fake_prospect = generate_fake_prospect()
            fake_prospect['source'] = 'test_data'
            
            try:
                prospect = db_service.create_prospect(fake_prospect)
                click.echo(f"{i+1}. Created: {prospect.full_name}")
            except Exception as e:
                click.echo(f"{i+1}. Failed: {str(e)}")
        
        click.echo(f"✅ Test data generation completed!")
        db_service.close()
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        logger.error("Test data generation failed", error=str(e))


@cli.command()
def config():
    """Show current configuration."""
    click.echo("⚙️ LinkedIn Outreach Automation Configuration\n")
    
    click.echo("📧 CREDENTIALS")
    click.echo(f"   LinkedIn Email: {'✅ Set' if settings.linkedin_email else '❌ Not set'}")
    click.echo(f"   LinkedIn Password: {'✅ Set' if settings.linkedin_password else '❌ Not set'}")
    click.echo()
    
    click.echo("🎯 AUTOMATION LIMITS")
    click.echo(f"   Daily Connection Requests: {settings.max_connection_requests_per_day}")
    click.echo(f"   Daily Messages: {settings.max_messages_per_day}")
    click.echo(f"   Delay Between Actions: {settings.delay_between_actions_min}-{settings.delay_between_actions_max}s")
    click.echo()
    
    click.echo("🔒 SECURITY SETTINGS")
    click.echo(f"   Rate Limiting: {'✅ Enabled' if settings.rate_limit_enabled else '❌ Disabled'}")
    click.echo(f"   Headless Browser: {'✅ Enabled' if settings.headless_browser else '❌ Disabled'}")
    click.echo()
    
    click.echo("💾 DATABASE")
    click.echo(f"   Database URL: {settings.database_url}")
    click.echo()
    
    click.echo("📝 LOGGING")
    click.echo(f"   Log Level: {settings.log_level}")
    click.echo(f"   Log File: {settings.log_file}")


if __name__ == "__main__":
    cli()