"""Create new tables for the Shaggy Dog project without affecting existing tables."""

from __future__ import annotations

from app import create_app, db
from app.models import User, DogTransformation


def create_shaggy_dog_tables() -> None:
    """Create only the tables needed for Shaggy Dog project."""
    app = create_app()

    with app.app_context():
        print("Checking existing tables...")

        # Get existing tables
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"Existing tables in database: {existing_tables}")

        print("\n" + "=" * 50)
        print("Creating Shaggy Dog tables...")
        print("=" * 50)

        # Create only our specific tables
        tables_to_create = ['dog_users', 'dog_transformations']

        for table_name in tables_to_create:
            if table_name in existing_tables:
                print(f"\n⚠ Table '{table_name}' already exists")
                response = input(f"Drop and recreate '{table_name}'? (yes/no): ")

                if response.lower() == 'yes':
                    # Drop specific table
                    if table_name == 'dog_users':
                        User.__table__.drop(db.engine, checkfirst=True)
                        print(f"✓ Dropped table '{table_name}'")
                    elif table_name == 'dog_transformations':
                        DogTransformation.__table__.drop(db.engine, checkfirst=True)
                        print(f"✓ Dropped table '{table_name}'")
                else:
                    print(f"Skipping '{table_name}'")
                    continue

        # Create the tables
        print("\nCreating tables...")
        User.__table__.create(db.engine, checkfirst=True)
        print("✓ Created 'dog_users' table")

        DogTransformation.__table__.create(db.engine, checkfirst=True)
        print("✓ Created 'dog_transformations' table")

        # Verify tables were created
        print("\n" + "=" * 50)
        print("Verifying table structure...")
        print("=" * 50)

        inspector = db.inspect(db.engine)

        if 'dog_users' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('dog_users')]
            print(f"\n✓ 'dog_users' table structure:")
            for col_info in inspector.get_columns('dog_users'):
                print(f"  - {col_info['name']}: {col_info['type']}")

        if 'dog_transformations' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('dog_transformations')]
            print(f"\n✓ 'dog_transformations' table structure:")
            for col_info in inspector.get_columns('dog_transformations'):
                print(f"  - {col_info['name']}: {col_info['type']}")

        print("\n" + "=" * 50)
        print("Shaggy Dog tables created successfully!")
        print("Other existing tables remain untouched.")
        print("=" * 50)


if __name__ == '__main__':
    create_shaggy_dog_tables()