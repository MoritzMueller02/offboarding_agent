-- Migration 01: Enable required extensions
-- Created: 2026-02-13

-- Vector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Full-text search support
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";