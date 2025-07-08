#!/usr/bin/env python

"""
Database migration script for AI-Enhanced Crypto Wallet Backend (Beta)

This script creates and updates database tables based on SQLAlchemy models.
It should be run whenever models are changed or when setting up a new environment.

Usage:
    python scripts/migrate.py [--reset]

Options:
    --reset     Drop all tables before creating them again (use with caution)
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import DropTable, MetaData

# Load environment variables
load_dotenv()

# Import models (add all your model imports here)
from app.models.portfolio import Base as PortfolioBase

# Combine all model bases (if you have multiple)
Base = declarative_base()
Base.metadata = PortfolioBase.metadata


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables before creating them again",
    )
    args = parser.parse_args()

    # Get database URL from environment variables
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable is not set.")
        print("   Please run 'source .env' or set the variable manually.")
        sys.exit(1)

    # Create database engine
    engine = create_engine(database_url)
    inspector = inspect(engine)

    # Check if tables exist
    existing_tables = inspector.get_table_names()
    model_tables = Base.metadata.tables.keys()

    # Drop tables if reset flag is provided
    if args.reset:
        confirm = input("⚠️  WARNING: This will delete all data. Are you sure? (y/N): ")
        if confirm.lower() != "y":
            print("Operation cancelled.")
            sys.exit(0)

        print("🗑️  Dropping all tables...")
        Base.metadata.drop_all(engine)
        print("✅ Tables dropped successfully.")

    # Create tables
    print("🏗️  Creating tables...")
    Base.metadata.create_all(engine)

    # Check which tables were created
    new_existing_tables = inspector.get_table_names()
    newly_created = set(new_existing_tables) - set(existing_tables)

    if newly_created:
        print(f"✅ Created {len(newly_created)} new tables: {', '.join(newly_created)}")
    else:
        print("ℹ️  No new tables were created.")

    print("✅ Migration completed successfully.")


if __name__ == "__main__":
    main()
