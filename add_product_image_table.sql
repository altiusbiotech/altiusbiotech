-- Migration: Add product_image table for image gallery
-- Created: 2026-01-13
-- Purpose: Allow multiple images per product with carousel/gallery feature

-- Create the product_image table
CREATE TABLE IF NOT EXISTS product_image (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    image_url VARCHAR(500),
    "order" INTEGER DEFAULT 0,
    caption VARCHAR(100)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_product_image_product_id ON product_image(product_id);
CREATE INDEX IF NOT EXISTS idx_product_image_order ON product_image("order");

-- Verify the table was created
SELECT table_name, column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'product_image'
ORDER BY ordinal_position;
