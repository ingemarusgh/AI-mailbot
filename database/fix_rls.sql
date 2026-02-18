-- ============================================================================
-- QUICK FIX: Aktivera RLS för users-tabellen
-- ============================================================================
-- Kör detta i Supabase SQL Editor om du redan kört setup.sql
-- Detta fixar säkerhetsvarningen "RLS is disabled"
-- ============================================================================

-- Aktivera RLS för users-tabellen
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Lägg till policies så att users bara kan se sin egen profil
DROP POLICY IF EXISTS "Users can view own profile" ON users;
CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (id = auth.uid());

DROP POLICY IF EXISTS "Users can update own profile" ON users;
CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (id = auth.uid());

-- ============================================================================
-- KLART! Gå till Table Editor och refresha - varningen ska vara borta!
-- ============================================================================
