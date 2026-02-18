# Database Setup - Supabase

## 📋 Schema Overview

Privacy-first design: **NO email content stored** - only hashed message IDs for duplicate prevention.

### Tables

- **companies** - Customer/tenant information
- **mail_configs** - IMAP/SMTP settings per company
- **ai_configs** - AI prompts and behavior per company
- **processed_emails** - SHA256 hashed message IDs only (no PII)
- **email_stats** - Aggregated anonymous statistics
- **users** - Admin users for frontend
- **company_users** - Multi-tenant access control

## 🚀 Setup Instructions

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note down:
   - Project URL (e.g., `https://xxxxx.supabase.co`)
   - `anon` key (for Lovable frontend)
   - `service_role` key (for Railway backend)

### 2. Apply Database Schema

1. Open Supabase Dashboard → SQL Editor
2. Run `schema.sql` first
3. Run `rls_policies.sql` second

Or use CLI:
```bash
supabase db push
```

### 3. Verify Setup

Check that tables are created:
```sql
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
```

Should show: `ai_configs, companies, company_users, email_stats, mail_configs, processed_emails, users`

## 🔑 Environment Variables

For Railway backend, set:
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbG...  # service_role key
OPENAI_API_KEY=sk-...
```

For Lovable frontend, set:
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbG...  # anon key
```

## 🔒 Security Notes

### Data Privacy
- **NO email content** is stored in database
- Only SHA256 hashes of message IDs for duplicate checking
- Email credentials encrypted in `mail_configs` table

### Access Control
- Row Level Security (RLS) enabled on all tables
- Users can only see their own companies' data
- Backend uses `service_role` key to bypass RLS (processes all companies)
- Frontend uses `anon` key with RLS enforcement

### Credential Storage
For production, use [Supabase Vault](https://supabase.com/docs/guides/database/vault) to encrypt `email_password`:

```sql
-- Example: Encrypt password with Vault
INSERT INTO mail_configs (company_id, email_password, ...)
VALUES (
    '...',
    vault.encrypt_text('actual-password', 'encryption-key-id'),
    ...
);
```

## 📊 Sample Data (Optional for Testing)

```sql
-- Insert test company
INSERT INTO companies (name, email, status)
VALUES ('Test Company AB', 'info@testcompany.se', 'active')
RETURNING id;

-- Insert mail config (use returned company_id)
INSERT INTO mail_configs (
    company_id, 
    imap_host, imap_port, 
    smtp_host, smtp_port,
    email_address, email_password
) VALUES (
    '<company_id_from_above>',
    'imap.gmail.com', 993,
    'smtp.gmail.com', 587,
    'test@testcompany.se', 'app-specific-password'
);

-- Insert AI config
INSERT INTO ai_configs (
    company_id,
    prompt_template,
    signature
) VALUES (
    '<company_id_from_above>',
    'You are a helpful assistant for {company_name}. Reply professionally to this email: {email_body}',
    'Med vänlig hälsning,\nTest Company AB\ntest@testcompany.se'
);
```

## 🔄 Migration Notes

From old JSON-based system:
- `sent_drafts.json` → `processed_emails` table
- `config.json` → `companies`, `mail_configs`, `ai_configs` tables
- File-based → Database-driven configuration
