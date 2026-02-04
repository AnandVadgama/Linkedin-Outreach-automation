"""
Setup script for LinkedIn Outreach Automation.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linkedin-outreach-automation",
    version="0.1.0",
    author="Lead Gen Professional",
    author_email="contact@leadgen.automation",
    description="Professional LinkedIn Outreach Automation Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leadgen/linkedin-outreach-automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "selenium>=4.15.2",
        "sqlalchemy>=2.0.23",
        "alembic>=1.12.1",
        "python-dotenv>=1.0.0",
        "structlog>=23.2.0",
        "click>=8.1.7",
        "pydantic>=2.5.0",
        "faker>=20.1.0",
        "webdriver-manager>=4.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "pre-commit>=3.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "linkedin-automation=src.cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)