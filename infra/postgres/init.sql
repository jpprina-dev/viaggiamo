-- PostgreSQL initialization script for Viaggiamo
-- This script runs when the database container is first created

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE viaggiamo_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'viaggiamo_db')\gexec

-- Connect to the database
\c viaggiamo_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Create a schema for the application (optional, for better organization)
-- CREATE SCHEMA IF NOT EXISTS viaggiamo;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE viaggiamo_db TO viaggiamo;
GRANT ALL PRIVILEGES ON SCHEMA public TO viaggiamo;

-- Create indexes for better performance (will be created by Alembic migrations)
-- These are just examples and will be handled by the ORM migrations

-- Add some helpful comments
COMMENT ON DATABASE viaggiamo_db IS 'Database for Viaggiamo carpooling MVP application';
