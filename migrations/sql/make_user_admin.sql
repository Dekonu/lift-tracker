-- Make a user a superuser (PostgreSQL)
-- Run in your PostgreSQL client after creating the user via the API

-- Replace 'admin@admin.com' with the email you used to sign up
UPDATE "user" 
SET is_superuser = true 
WHERE email = 'admin@admin.com';

-- Verify it worked
SELECT id, email, name, is_superuser 
FROM "user" 
WHERE email = 'admin@admin.com';

