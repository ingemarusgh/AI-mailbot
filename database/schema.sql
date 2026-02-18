-- AI Mailbot - Supabase Database Schema
-- Privacy-first design: NO email content stored, only hashed IDs

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies table - Customer/tenant information
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'paused')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Mail configuration per company
CREATE TABLE mail_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- IMAP settings
    imap_host TEXT NOT NULL,
    imap_port INTEGER NOT NULL DEFAULT 993,
    imap_use_ssl BOOLEAN NOT NULL DEFAULT true,
    inbox_folder TEXT NOT NULL DEFAULT 'INBOX',
    
    -- SMTP settings
    smtp_host TEXT NOT NULL,
    smtp_port INTEGER NOT NULL DEFAULT 587,
    smtp_use_tls BOOLEAN NOT NULL DEFAULT true,
    
    -- Credentials (will be encrypted)
    email_address TEXT NOT NULL,
    email_password TEXT NOT NULL, -- Use Supabase Vault in production
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(company_id)
);

-- AI configuration per company
CREATE TABLE ai_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- AI provider settings
    provider TEXT NOT NULL DEFAULT 'openai' CHECK (provider IN ('openai')),
    model TEXT NOT NULL DEFAULT 'gpt-3.5-turbo',
    
    -- Prompt and signature
    prompt_template TEXT NOT NULL,
    signature TEXT NOT NULL,
    
    -- Bot behavior
    check_interval INTEGER NOT NULL DEFAULT 300, -- seconds
    max_messages_per_check INTEGER NOT NULL DEFAULT 10,
    create_drafts BOOLEAN NOT NULL DEFAULT true,
    auto_send BOOLEAN NOT NULL DEFAULT false,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(company_id)
);

-- Processed emails - ONLY hashed IDs for duplicate prevention
-- NO email content, subject, sender, or any PII stored
CREATE TABLE processed_emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Privacy: Only SHA256 hashes stored, no actual email data
    message_hash TEXT NOT NULL, -- SHA256(message_id)
    thread_hash TEXT, -- SHA256(thread_id) if available
    
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Index for fast duplicate checking
    UNIQUE(company_id, message_hash)
);

-- Email statistics - Aggregated anonymous metrics
CREATE TABLE email_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Metrics
    emails_processed INTEGER NOT NULL DEFAULT 0,
    drafts_created INTEGER NOT NULL DEFAULT 0,
    errors INTEGER NOT NULL DEFAULT 0,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(company_id, date)
);

-- Users table - Admin users for Lovable frontend
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Company-User relationship - Multi-tenant access control
CREATE TABLE company_users (
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('owner', 'admin', 'viewer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (company_id, user_id)
);

-- Indexes for performance
CREATE INDEX idx_companies_status ON companies(status);
CREATE INDEX idx_processed_emails_company ON processed_emails(company_id, processed_at DESC);
CREATE INDEX idx_email_stats_company_date ON email_stats(company_id, date DESC);
CREATE INDEX idx_company_users_user ON company_users(user_id);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mail_configs_updated_at BEFORE UPDATE ON mail_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_configs_updated_at BEFORE UPDATE ON ai_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
