-- DATABASE MIGRATION SCRIPT - MAY 2026
-- This script applies the changes required for the updated Faculty Appraisal form.

-- 1. Updates for Part A: Contribution to Society
-- Rename 'label' to 'activity' and add 'status'
ALTER TABLE public.social_contributions RENAME COLUMN label TO activity;
ALTER TABLE public.social_contributions ADD COLUMN status TEXT;

-- 2. Updates for Part B: Patents (IPR)
-- Add 'scope' for National / International status
ALTER TABLE public.patents ADD COLUMN scope TEXT;

-- 3. Update Form Section Definitions (Metadata)
-- This ensures the backend 'shredding' process knows about the new fields and titles.

-- Update 'Contribution to Society' definition
UPDATE public.form_section_definitions 
SET fields = '["activity","status","details"]'
WHERE section_key = 'society';

-- Update 'Patents (IPR)' definition to include 'scope'
UPDATE public.form_section_definitions 
SET fields = '["title","type","scope","patent_date","patent_status","file_no"]'
WHERE section_key = 'patents';

-- Update Section Titles to match new form images
UPDATE public.form_section_definitions 
SET title = 'B8(a). FDP / Workshops'
WHERE section_key = 'fdps';

UPDATE public.form_section_definitions 
SET title = 'B8(b). Industrial Training'
WHERE section_key = 'training';

-- Note: The 'IPR / Copyright / Patent' (ipr_records) already had a 'scope' field in the schema, 
-- but we ensure its metadata is also up to date if needed.
UPDATE public.form_section_definitions 
SET fields = '["title","scope","ipr_date","ipr_status","file_no"]'
WHERE section_key = 'ipr';
