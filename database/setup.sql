-- ============================================================================
-- AI MAILBOT - COMPLETE SUPABASE SETUP
-- ============================================================================
-- Kör denna fil EN gång i Supabase SQL Editor för att sätta upp allt
-- 
-- Detta skapar:
-- 1. Alla databas-tabeller
-- 2. Row Level Security (RLS) policies
-- 3. Indexes för prestanda
-- 4. Triggers för auto-update timestamps
--
-- Privacy-first: INGEN email-data lagras, bara hashade IDs!
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABELLER
-- ============================================================================

-- Companies table - Customer/tenant information
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'paused')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Mail configuration per company
CREATE TABLE IF NOT EXISTS mail_configs (
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
CREATE TABLE IF NOT EXISTS ai_configs (
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
CREATE TABLE IF NOT EXISTS processed_emails (
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
CREATE TABLE IF NOT EXISTS email_stats (
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
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Company-User relationship - Multi-tenant access control
CREATE TABLE IF NOT EXISTS company_users (
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('owner', 'admin', 'viewer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (company_id, user_id)
);

-- ============================================================================
-- INDEXES FÖR PRESTANDA
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);
CREATE INDEX IF NOT EXISTS idx_processed_emails_company ON processed_emails(company_id, processed_at DESC);
CREATE INDEX IF NOT EXISTS idx_email_stats_company_date ON email_stats(company_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_company_users_user ON company_users(user_id);

-- ============================================================================
-- AUTO-UPDATE TRIGGERS
-- ============================================================================

-- Function för att uppdatera updated_at automatiskt
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Applicera trigger på tabeller
DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at 
    BEFORE UPDATE ON companies
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_mail_configs_updated_at ON mail_configs;
CREATE TRIGGER update_mail_configs_updated_at 
    BEFORE UPDATE ON mail_configs
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ai_configs_updated_at ON ai_configs;
CREATE TRIGGER update_ai_configs_updated_at 
    BEFORE UPDATE ON ai_configs
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE mail_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE processed_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_users ENABLE ROW LEVEL SECURITY;

-- Companies: Users can only see companies they have access to
DROP POLICY IF EXISTS "Users can view their companies" ON companies;
CREATE POLICY "Users can view their companies"
    ON companies FOR SELECT
    USING (
        id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Admins can insert companies" ON companies;
CREATE POLICY "Admins can insert companies"
    ON companies FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

DROP POLICY IF EXISTS "Company owners can update their companies" ON companies;
CREATE POLICY "Company owners can update their companies"
    ON companies FOR UPDATE
    USING (
        id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
    );

-- Mail configs: Same access as companies
DROP POLICY IF EXISTS "Users can view their mail configs" ON mail_configs;
CREATE POLICY "Users can view their mail configs"
    ON mail_configs FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Company admins can manage mail configs" ON mail_configs;
CREATE POLICY "Company admins can manage mail configs"
    ON mail_configs FOR ALL
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
    );

-- AI configs: Same access as companies
DROP POLICY IF EXISTS "Users can view their AI configs" ON ai_configs;
CREATE POLICY "Users can view their AI configs"
    ON ai_configs FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Company admins can manage AI configs" ON ai_configs;
CREATE POLICY "Company admins can manage AI configs"
    ON ai_configs FOR ALL
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
    );

-- Processed emails: Read-only for users
DROP POLICY IF EXISTS "Users can view their processed emails" ON processed_emails;
CREATE POLICY "Users can view their processed emails"
    ON processed_emails FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

-- Email stats: Read-only for users
DROP POLICY IF EXISTS "Users can view their email stats" ON email_stats;
CREATE POLICY "Users can view their email stats"
    ON email_stats FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

-- Company users: Users can see relationships for their companies
DROP POLICY IF EXISTS "Users can view their company relationships" ON company_users;
CREATE POLICY "Users can view their company relationships"
    ON company_users FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Company owners can manage users" ON company_users;
CREATE POLICY "Company owners can manage users"
    ON company_users FOR ALL
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid() AND role = 'owner'
        )
    );

-- ============================================================================
-- FÄRDIG!
-- ============================================================================
-- Databasen är nu redo för AI Mailbot!
-- 
-- Nästa steg:
-- 1. Lägg till testdata (se nedan) ELLER
-- 2. Använd Lovable admin UI för att lägga till företag
-- ============================================================================
