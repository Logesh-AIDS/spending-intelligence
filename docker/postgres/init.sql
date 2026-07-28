-- PostgreSQL initialization
-- Alembic handles schema creation via migrations
-- This file sets up extensions and performance settings

CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- for fuzzy text search
CREATE EXTENSION IF NOT EXISTS btree_gin; -- for composite indexes

-- Connection settings for production
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '16MB';
