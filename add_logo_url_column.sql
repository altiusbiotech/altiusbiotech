-- Migration: Add logo_url column to content table
-- Created: 2026-09-21
-- Purpose: Store the Cloudinary URL for an uploaded logo so it survives redeploys
--          (falls back to static/images/logo.jpg when NULL)

ALTER TABLE content ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);

-- Verify
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'content' AND column_name = 'logo_url';
