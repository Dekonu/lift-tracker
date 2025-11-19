-- Create admin user in Supabase
-- Run this in Supabase SQL Editor

-- First, check if admin user exists
SELECT id, email, name, is_superuser 
FROM "user" 
WHERE email = 'admin@admin.com';

-- If user doesn't exist, create it
-- Note: You'll need to hash the password first using bcrypt
-- For now, you can use the backend API to create the user, or use this SQL:
-- (You'll need to replace the hashed_password with the actual bcrypt hash)

-- Option 1: Create via API (recommended)
-- POST to http://localhost:8000/api/v1/user with:
-- {
--   "name": "admin",
--   "email": "admin@admin.com",
--   "password": "!Ch4ng3Th1sP4ssW0rd!"
-- }
-- Then update the user to be superuser:

-- Option 2: Update existing user to superuser
UPDATE "user" 
SET is_superuser = true 
WHERE email = 'admin@admin.com';

-- Verify the admin user
SELECT id, email, name, is_superuser 
FROM "user" 
WHERE email = 'admin@admin.com';

