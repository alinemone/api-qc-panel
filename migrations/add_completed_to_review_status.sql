-- Migration: Add 'completed' to analysis_review_status enum

-- Add 'completed' to the enum if it doesn't already exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_enum
        WHERE enumlabel = 'completed'
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'analysis_review_status')
    ) THEN
        ALTER TYPE analysis_review_status ADD VALUE 'completed';
    END IF;
END $$;

-- Update existing 'approved' records to 'completed' (optional, uncomment if needed)
-- UPDATE conversation_analysis SET review_status = 'completed' WHERE review_status = 'approved';
