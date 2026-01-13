"""
Create product_image table for gallery feature
Run this script to add the gallery table to your database
"""

from app import app, db
from models import ProductImage

print("Creating product_image table...")

with app.app_context():
    # Create all tables (including product_image)
    db.create_all()
    print("✅ Tables created successfully!")

    # Verify the table exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    if 'product_image' in tables:
        print("✅ product_image table exists!")

        # Show columns
        columns = inspector.get_columns('product_image')
        print("\nColumns in product_image table:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("❌ product_image table NOT found!")
        print(f"Available tables: {tables}")

print("\nDone! You can now upload multiple images per product.")
