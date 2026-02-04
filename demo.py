#!/usr/bin/env python3
"""
Demo script for LinkedIn Outreach Automation v0.1.0
Shows the key functionality and features of the platform.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core import settings, get_logger
from src.models import init_database, check_database_exists, ProspectStatus
from src.services import DatabaseService
from src.utils import generate_fake_prospect


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("🚀 LinkedIn Outreach Automation - Demo Script")
    print("   Version 0.1.0 - Core Infrastructure & Basic Outreach")
    print("=" * 60)
    print()


def setup_demo_environment():
    """Setup demo environment."""
    print("🔧 Setting up demo environment...")
    
    # Initialize database if needed
    if not check_database_exists():
        print("   📊 Initializing database...")
        init_database()
        print("   ✅ Database created!")
    else:
        print("   ✅ Database already exists!")
    
    print("   ✅ Demo environment ready!")
    print()


def demonstrate_prospect_management():
    """Demonstrate prospect management features."""
    print("👥 PROSPECT MANAGEMENT DEMO")
    print("-" * 40)
    
    db_service = DatabaseService()
    
    # Generate some demo prospects
    print("Creating demo prospects...")
    prospects_created = 0
    
    for i in range(5):
        fake_prospect = generate_fake_prospect()
        fake_prospect['source'] = 'demo_script'
        
        try:
            prospect = db_service.create_prospect(fake_prospect)
            prospects_created += 1
            print(f"   ✅ {prospect.full_name} ({prospect.company})")
        except Exception as e:
            print(f"   ⚠️  Skipped duplicate prospect")
    
    print(f"\n📊 Created {prospects_created} new demo prospects!")
    
    # Show prospect statistics
    stats = db_service.get_prospect_stats()
    print("\n📈 Current Database Stats:")
    print(f"   Total Prospects: {stats['total_prospects']}")
    print(f"   New: {stats['prospects_new']}")
    print(f"   Contacted: {stats['prospects_contacted']}")
    print(f"   Connected: {stats['prospects_connected']}")
    
    # Demonstrate status updates
    new_prospects = db_service.get_prospects_by_status(
        ProspectStatus.NEW, limit=2
    )
    
    if new_prospects:
        print(f"\n🔄 Updating status for 2 prospects...")
        for prospect in new_prospects:
            db_service.update_prospect_status(
                prospect.id,
                ProspectStatus.CONTACTED
            )
            print(f"   ✅ {prospect.full_name} -> CONTACTED")
    
    db_service.close()
    print()


def demonstrate_automation_features():
    """Demonstrate automation safety features."""
    print("🤖 AUTOMATION FEATURES DEMO")
    print("-" * 40)
    
    # Show configuration
    print("Current automation settings:")
    print(f"   Daily Connection Limit: {settings.max_connection_requests_per_day}")
    print(f"   Daily Message Limit: {settings.max_messages_per_day}")
    print(f"   Action Delay: {settings.delay_between_actions_min}-{settings.delay_between_actions_max}s")
    print(f"   Rate Limiting: {'✅ Enabled' if settings.rate_limit_enabled else '❌ Disabled'}")
    print(f"   Headless Browser: {'✅ Enabled' if settings.headless_browser else '❌ Disabled'}")
    
    # Show safety features
    print("\n🛡️ Built-in Safety Features:")
    print("   ✅ Rate limiting to protect your LinkedIn account")
    print("   ✅ Random delays between actions (30-120 seconds)")
    print("   ✅ Daily limits for connections and messages") 
    print("   ✅ Dry-run mode for testing")
    print("   ✅ Comprehensive error handling")
    print("   ✅ Activity logging and monitoring")
    print()


def demonstrate_cli_features():
    """Demonstrate CLI features."""
    print("💻 COMMAND-LINE INTERFACE DEMO")
    print("-" * 40)
    
    print("Available CLI commands:")
    print()
    
    commands = [
        ("init-db", "Initialize the database"),
        ("search-prospects", "Search LinkedIn for prospects"),
        ("send-connections", "Send connection requests"),
        ("list-prospects", "List all prospects in database"),
        ("stats", "Show automation statistics"),
        ("generate-test-data", "Generate fake data for testing"),
        ("config", "Show current configuration"),
    ]
    
    for cmd, desc in commands:
        print(f"   📋 {cmd:<20} - {desc}")
    
    print("\n💡 Example usage:")
    print("   python -m src.cli.main search-prospects --keywords 'software engineer' --save")
    print("   python -m src.cli.main send-connections --limit 5 --dry-run")
    print("   python -m src.cli.main stats")
    print()


def demonstrate_architecture():
    """Show architecture and code quality."""
    print("🏗️ ARCHITECTURE & CODE QUALITY")
    print("-" * 40)
    
    print("Project structure:")
    structure = [
        "src/core/          # Configuration, logging, exceptions",
        "src/models/        # SQLAlchemy database models",  
        "src/services/      # Business logic (LinkedIn, Database)",
        "src/utils/         # Helper functions and utilities",
        "src/cli/           # Command-line interface",
        "tests/             # Comprehensive test suite",
    ]
    
    for item in structure:
        print(f"   📁 {item}")
    
    print("\n✨ Code Quality Features:")
    quality_features = [
        "Industry-standard folder structure",
        "Modular, testable architecture", 
        "Type hints with Pydantic validation",
        "Comprehensive error handling",
        "Structured logging with rotation",
        "90%+ test coverage target",
        "Black + isort + flake8 formatting",
        "Professional documentation"
    ]
    
    for feature in quality_features:
        print(f"   ✅ {feature}")
    print()


def show_roadmap():
    """Show future development roadmap."""
    print("🗺️ DEVELOPMENT ROADMAP")
    print("-" * 40)
    
    print("📦 Version 0.2 - Campaign Management & Templates")
    v02_features = [
        "Campaign creation and management",
        "Message templates with variables",
        "Follow-up automation sequences", 
        "Web dashboard UI",
        "Email notifications",
        "Advanced filtering and segmentation"
    ]
    
    for feature in v02_features:
        print(f"   🔲 {feature}")
    
    print("\n📦 Version 0.3 - Advanced Analytics & Optimization")
    v03_features = [
        "A/B testing for messages",
        "Lead scoring algorithms",
        "Advanced reporting dashboard",
        "CRM integrations (HubSpot, Salesforce)",
        "REST API endpoints", 
        "Machine learning insights"
    ]
    
    for feature in v03_features:
        print(f"   🔲 {feature}")
    print()


def print_conclusion():
    """Print conclusion and next steps."""
    print("🎯 DEMO CONCLUSION")
    print("-" * 40)
    
    print("✅ LinkedIn Outreach Automation v0.1.0 successfully demonstrates:")
    print("   • Professional-grade architecture and code quality")
    print("   • Comprehensive prospect management system") 
    print("   • Safe automation with built-in protections")
    print("   • User-friendly command-line interface")
    print("   • Robust testing and error handling")
    print("   • Industry best practices and documentation")
    
    print("\n🚀 Next Steps:")
    print("   1. Set up your LinkedIn credentials in .env")
    print("   2. Run: python -m src.cli.main search-prospects --help")
    print("   3. Test with: python -m src.cli.main send-connections --dry-run")
    print("   4. Monitor logs in logs/ directory")
    print("   5. Star the project if you found it useful! ⭐")
    
    print("\n⚠️  Important Reminder:")
    print("   Always comply with LinkedIn's Terms of Service")
    print("   Use reasonable rate limits and monitor your account")
    print("   This tool is for legitimate business purposes only")
    
    print("\n" + "=" * 60)
    print("🙏 Thank you for trying LinkedIn Outreach Automation!")
    print("   For questions: contact@leadgen.automation")
    print("=" * 60)


def main():
    """Run the complete demo."""
    try:
        print_banner()
        setup_demo_environment()
        demonstrate_prospect_management()
        demonstrate_automation_features()
        demonstrate_cli_features()
        demonstrate_architecture()
        show_roadmap()
        print_conclusion()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        print("Please check your setup and try again")


if __name__ == "__main__":
    main()