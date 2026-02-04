# LinkedIn Outreach Automation - Version 0.1.0

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Version 0.1** - Core Infrastructure & Basic Outreach

A professional-grade LinkedIn outreach automation platform built with modular architecture and industry best practices.

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd linkedin-outreach-automation

# 2. Setup the project
make setup

# 3. Edit your LinkedIn credentials
nano .env

# 4. Generate test data
make test-data

# 5. View your prospects
make prospects

# 6. Check stats
make stats
```

## 🚀 Features (v0.1)

- **Prospect Management**: Store and manage LinkedIn prospects
- **Basic Automation**: Automated connection requests
- **Database Integration**: SQLite with SQLAlchemy ORM
- **Configuration Management**: Environment-based settings
- **Comprehensive Logging**: Structured logging with rotation
- **Error Handling**: Robust error handling and recovery

## 🏗️ Architecture

```
linkedin-outreach-automation/
├── src/
│   ├── core/              # Core business logic
│   ├── models/            # Data models
│   ├── services/          # External service integrations
│   ├── utils/             # Utility functions
│   └── cli/               # Command-line interface
├── tests/                 # Test suite
├── config/               # Configuration files
├── logs/                 # Application logs
└── data/                 # Database and data files
```

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **Database**: SQLite + SQLAlchemy ORM
- **HTTP**: requests + selenium (for LinkedIn interaction)
- **Configuration**: python-dotenv
- **Logging**: structlog
- **Testing**: pytest
- **Code Quality**: black, isort, flake8

## 🧪 Testing

```bash
# Run tests
make test

# Run with coverage
make coverage

# Check code quality
make check
```

## 🎯 CLI Usage Examples

```bash
# Search for prospects
python -m src.cli.main search-prospects --keywords "software engineer" --location "San Francisco" --save

# Send connection requests (dry run first)
python -m src.cli.main send-connections --limit 5 --dry-run

# Send actual connection requests  
python -m src.cli.main send-connections --limit 5 --message "Hi, I'd love to connect!"

# View statistics
python -m src.cli.main stats

# List all prospects
python -m src.cli.main list-prospects
```

## ⚠️ Important Notes

### LinkedIn Terms of Service
- This tool is for educational and legitimate business purposes only
- Always comply with LinkedIn's Terms of Service and User Agreement
- Use reasonable rate limits to avoid account restrictions
- Consider LinkedIn's Premium/Sales Navigator for official automation

### Security & Best Practices
- Never commit credentials to version control
- Use strong passwords and enable 2FA on your LinkedIn account
- Monitor your daily automation limits
- Always test with `--dry-run` flag first

### Rate Limiting
The tool includes built-in safety features:
- Daily connection request limits (default: 20/day)
- Random delays between actions (30-120 seconds)
- Headless browser option for discretion

## 📋 Roadmap

- **v0.1**: Core Infrastructure & Basic Outreach ✅
- **v0.2**: Campaign Management & Templates (Next)
- **v0.3**: Advanced Analytics & A/B Testing (Future)

## 📊 Version History

- **v0.1.0** (2024-02) - Initial release with core automation features