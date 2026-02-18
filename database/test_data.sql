-- ============================================================================
-- TEST DATA - Exempelföretag för att testa systemet
-- ============================================================================
-- KÖR DETTA EFTER setup.sql om du vill ha testdata
-- Annars lägg till företag via Lovable admin UI
-- ============================================================================

-- Insert test company
INSERT INTO companies (name, email, status)
VALUES ('Test Company AB', 'info@testcompany.se', 'active')
RETURNING id;

-- OBS! Ersätt <COMPANY_ID> nedan med UUID som returnerades ovan
-- Eller kör denna query för att få ID:
-- SELECT id FROM companies WHERE email = 'info@testcompany.se';

-- Insert mail config (ÄNDRA TILL DINA RIKTIGA CREDENTIALS!)
INSERT INTO mail_configs (
    company_id,
    imap_host,
    imap_port,
    imap_use_ssl,
    smtp_host,
    smtp_port,
    smtp_use_tls,
    email_address,
    email_password,
    inbox_folder
) VALUES (
    '<COMPANY_ID>',  -- Ändra detta!
    'imap.gmail.com',
    993,
    true,
    'smtp.gmail.com',
    587,
    true,
    'info@testcompany.se',  -- Ändra detta!
    'your-app-specific-password',  -- Ändra detta!
    'INBOX'
);

-- Insert AI config
INSERT INTO ai_configs (
    company_id,
    provider,
    model,
    prompt_template,
    signature,
    check_interval,
    max_messages_per_check,
    create_drafts,
    auto_send
) VALUES (
    '<COMPANY_ID>',  -- Ändra detta!
    'openai',
    'gpt-3.5-turbo',
    'Du är en hjälpsam assistent för {company_name}. Svara professionellt och vänligt på följande email:

{email_body}

Håll svaret kort och koncist.',
    'Med vänlig hälsning,
Test Company AB
info@testcompany.se
www.testcompany.se',
    300,  -- 5 minuter mellan checks
    10,   -- Max 10 mail per check
    true,  -- Skapa drafts
    false  -- Skicka INTE automatiskt
);

-- ============================================================================
-- Verifiera att allt fungerar:
-- ============================================================================

-- Kolla att företaget skapades:
SELECT * FROM companies WHERE email = 'info@testcompany.se';

-- Kolla att konfigurationen är komplett:
SELECT 
    c.name,
    c.email,
    c.status,
    mc.imap_host,
    mc.smtp_host,
    ac.model,
    ac.check_interval
FROM companies c
LEFT JOIN mail_configs mc ON c.id = mc.company_id
LEFT JOIN ai_configs ac ON c.id = ac.company_id
WHERE c.email = 'info@testcompany.se';

-- Om du ser alla värden är allt klart! 🎉
