-- Migration: Replace fixed social-link columns with a manageable social_link table
-- Created: 2026-09-21
-- Purpose: Let admins add/remove/reorder any number of social links (not just FB/LinkedIn/Instagram)

CREATE TABLE IF NOT EXISTS social_link (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL,
    "order" INTEGER DEFAULT 0
);

-- Drop the old fixed columns (superseded by social_link table)
ALTER TABLE content DROP COLUMN IF EXISTS facebook_url;
ALTER TABLE content DROP COLUMN IF EXISTS linkedin_url;
ALTER TABLE content DROP COLUMN IF EXISTS instagram_url;

-- Verify
SELECT table_name, column_name FROM information_schema.columns WHERE table_name = 'social_link' ORDER BY ordinal_position;
