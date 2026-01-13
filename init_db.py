"""Initialize production database (run once after deployment)."""

from __future__ import annotations

import os


def init_production_database() -> None:
    """Initialize the production database on Render."""
    from app import create_app, db
    from app.models import User, DogTransformation

    # Force production mode
    os.environ['FLASK_ENV'] = 'production'

    app = create_app('production')

    with app.app_context():
        print("Initializing Production Database")
        print("="*50)

        # Get database URL
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        print(f"Database: {db_url[:30]}...")

        # Get existing tables
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()

        print(f"\nAll existing tables in database: {existing_tables}")

        # Check if our specific tables exist
        our_tables = ['dog_users', 'dog_transformations']
        existing_our_tables = [t for t in our_tables if t in existing_tables]

        if existing_our_tables:
            print(f"\nShaggy Dog tables found: {existing_our_tables}")
            response = input("\nRecreate Shaggy Dog tables? (yes/no): ")

            if response.lower() != 'yes':
                print("Database initialization cancelled.")
                return

            print("\nDropping Shaggy Dog tables...")
            # Drop in correct order (child tables first)
            DogTransformation.__table__.drop(db.engine, checkfirst=True)
            User.__table__.drop(db.engine, checkfirst=True)
            print("✓ Dropped Shaggy Dog tables")

        # Create our tables
        print("\nCreating Shaggy Dog tables...")
        User.__table__.create(db.engine, checkfirst=True)
        print("✓ Created 'dog_users' table")

        DogTransformation.__table__.create(db.engine, checkfirst=True)
        print("✓ Created 'dog_transformations' table")

        # Verify our tables
        inspector = db.inspect(db.engine)

        print("\n" + "="*50)
        print("Shaggy Dog Tables Structure:")
        print("="*50)

        if 'dog_users' in inspector.get_table_names():
            print(f"\n✓ dog_users")
            columns = inspector.get_columns('dog_users')
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")

        if 'dog_transformations' in inspector.get_table_names():
            print(f"\n✓ dog_transformations")
            columns = inspector.get_columns('dog_transformations')
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")

            # Show foreign keys
            fks = inspector.get_foreign_keys('dog_transformations')
            if fks:
                print(f"\n  Foreign Keys:")
                for fk in fks:
                    print(f"    - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")

        print("\n" + "="*50)
        print("Production database initialized successfully!")
        print("="*50)
        print("\nIMPORTANT: Other tables in the database remain untouched.")
        print("You can now use the Shaggy Dog application.")


if __name__ == '__main__':
    init_production_database()