-- Migration: Add social link columns to content table
-- Created: 2026-09-21
-- Purpose: Allow admin to set Facebook/LinkedIn/Instagram URLs shown in footer

ALTER TABLE content ADD COLUMN IF NOT EXISTS facebook_url VARCHAR(255);
ALTER TABLE content ADD COLUMN IF NOT EXISTS linkedin_url VARCHAR(255);
ALTER TABLE content ADD COLUMN IF NOT EXISTS instagram_url VARCHAR(255);

-- Verify the columns were added
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'content'
  AND column_name IN ('facebook_url', 'linkedin_url', 'instagram_url');
