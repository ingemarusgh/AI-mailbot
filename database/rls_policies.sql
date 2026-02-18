-- Row Level Security (RLS) Policies
-- Ensures users can only see their own companies' data

-- Enable RLS on all tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE mail_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE processed_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_users ENABLE ROW LEVEL SECURITY;

-- Companies: Users can only see companies they have access to
CREATE POLICY "Users can view their companies"
    ON companies FOR SELECT
    USING (
        id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Admins can insert companies"
    ON companies FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Company owners can update their companies"
    ON companies FOR UPDATE
    USING (
        id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
    );

-- Mail configs: Same access as companies
CREATE POLICY "Users can view their mail configs"
    ON mail_configs FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Company admins can manage mail configs"
    ON mail_configs FOR ALL
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
    );

-- AI configs: Same access as companies
CREATE POLICY "Users can view their AI configs"
    ON ai_configs FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Company admins can manage AI configs"
    ON ai_configs FOR ALL
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
        )
    );

-- Processed emails: Read-only for users
CREATE POLICY "Users can view their processed emails"
    ON processed_emails FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

-- Email stats: Read-only for users
CREATE POLICY "Users can view their email stats"
    ON email_stats FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

-- Company users: Users can see relationships for their companies
CREATE POLICY "Users can view their company relationships"
    ON company_users FOR SELECT
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Company owners can manage users"
    ON company_users FOR ALL
    USING (
        company_id IN (
            SELECT company_id FROM company_users
            WHERE user_id = auth.uid() AND role = 'owner'
        )
    );

-- Service role bypass (for Railway backend)
-- The backend will use service_role key to bypass RLS
-- and process emails for all companies
