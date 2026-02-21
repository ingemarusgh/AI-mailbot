-- OAuth2 Migration for Azure AD Integration
-- Run this in Supabase SQL Editor

-- Step 1: Add OAuth2 columns to mail_configs
ALTER TABLE mail_configs
ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50) DEFAULT 'azure',
ADD COLUMN IF NOT EXISTS access_token TEXT,
ADD COLUMN IF NOT EXISTS refresh_token TEXT,
ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMP WITH TIME ZONE;

-- Step 2: Make email_password optional (for OAuth2 accounts)
ALTER TABLE mail_configs
ALTER COLUMN email_password DROP NOT NULL;

-- Step 3: Add constraint to ensure either password OR oauth tokens
ALTER TABLE mail_configs
ADD CONSTRAINT check_auth_method CHECK (
  (email_password IS NOT NULL) OR 
  (access_token IS NOT NULL AND refresh_token IS NOT NULL)
);

-- Step 4: Create index for token expiry checks (performance)
CREATE INDEX IF NOT EXISTS idx_mail_configs_token_expiry 
ON mail_configs(token_expires_at) 
WHERE oauth_provider IS NOT NULL;

-- Step 5: Add comment for documentation
COMMENT ON COLUMN mail_configs.oauth_provider IS 'OAuth2 provider: azure, google, or NULL for password auth';
COMMENT ON COLUMN mail_configs.access_token IS 'OAuth2 access token (encrypted in app layer)';
COMMENT ON COLUMN mail_configs.refresh_token IS 'OAuth2 refresh token (encrypted in app layer)';
COMMENT ON COLUMN mail_configs.token_expires_at IS 'When access_token expires (UTC timestamp)';

-- Step 6: Create function to check if token needs refresh
CREATE OR REPLACE FUNCTION needs_token_refresh(config_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM mail_configs
    WHERE id = config_id
    AND oauth_provider IS NOT NULL
    AND (token_expires_at IS NULL OR token_expires_at < NOW() + INTERVAL '5 minutes')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 7: Grant execute permission on function
GRANT EXECUTE ON FUNCTION needs_token_refresh TO authenticated, service_role;

-- Migration complete!
-- Verify with: SELECT * FROM mail_configs LIMIT 1;
