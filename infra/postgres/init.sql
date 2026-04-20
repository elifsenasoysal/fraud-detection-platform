-- ============================================
-- Fraud Detection Platform — Initial Database Schema
-- ============================================
-- This script runs on first PostgreSQL container startup

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE transaction_status AS ENUM ('approved', 'suspicious', 'rejected');
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical');

-- ──────────────────────────────────────────
-- Users table
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    risk_level risk_level DEFAULT 'low',
    total_transactions INTEGER DEFAULT 0,
    total_fraud_flags INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ──────────────────────────────────────────
-- Transactions table
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'TRY',
    location VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    status transaction_status DEFAULT 'approved',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ──────────────────────────────────────────
-- Fraud alerts table
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fraud_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    risk_level risk_level NOT NULL,
    violated_rules TEXT[] NOT NULL,
    details JSONB DEFAULT '{}',
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ──────────────────────────────────────────
-- Indexes for query performance
-- ──────────────────────────────────────────
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_user_created ON transactions(user_id, created_at DESC);

CREATE INDEX idx_fraud_alerts_user_id ON fraud_alerts(user_id);
CREATE INDEX idx_fraud_alerts_created_at ON fraud_alerts(created_at DESC);
CREATE INDEX idx_fraud_alerts_is_resolved ON fraud_alerts(is_resolved);

CREATE INDEX idx_users_external_id ON users(external_id);
CREATE INDEX idx_users_risk_level ON users(risk_level);
