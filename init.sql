-- Initialize the mulligan_simulator database
-- This script runs when the PostgreSQL container starts

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the database if it doesn't exist (though it should already exist from environment)
-- This is just a safety check
SELECT 'Database initialization complete' as status;
