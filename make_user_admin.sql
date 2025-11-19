-- Make a user a superuser in Supabase
-- Run this in Supabase SQL Editor after creating the user via signup

-- Replace 'admin@admin.com' with the email you used to sign up
UPDATE "user" 
SET is_superuser = true 
WHERE email = 'admin@admin.com';

-- Verify it worked
SELECT id, email, name, is_superuser 
FROM "user" 
WHERE email = 'admin@admin.com';

