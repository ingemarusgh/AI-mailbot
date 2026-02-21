# 🔐 Lovable OAuth2 Setup - Microsoft 365 Integration

**Dark Cyberpunk Admin Panel med Azure AD OAuth2**

---

## 📋 STEG 1: Grundkonfiguration

Följ först stegen i `LOVABLE_SETUP.md` för:
- Skapa Lovable projekt
- Konfigurera Supabase connection
- Sätt upp dark cyberpunk tema

---

## 📋 STEG 2: Azure Environment Variables

I Lovable → **Settings** → **Environment Variables**, lägg till:

```bash
VITE_SUPABASE_URL=https://urauulfqtwfxvwmtsomd.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVyYXV1bGZxdHdmeHZ3bXRzb21kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0NDc2OTQsImV4cCI6MjA4NzAyMzY5NH0.rRpynHFcl52XRJqFRlve4uY0VYnUP7a_fM2QWiXJkok

# Azure AD OAuth2 (efter du skapat Azure App)
VITE_AZURE_CLIENT_ID=your_client_id_here
VITE_AZURE_TENANT_ID=common
VITE_AZURE_REDIRECT_URI=https://urauulfqtwfxvwmtsomd.supabase.co/auth/v1/callback
```

---

## 📋 STEG 3: OAuth2 Prompt för Lovable

### Design Prompt (grundläggande UI)

```
Create a dark cyberpunk admin dashboard for AI email bot with Microsoft 365 OAuth2 integration.

DESIGN THEME:
- Dark background (#0a0a0a, #1a1a1a)
- Neon cyan (#00f5ff) for primary actions
- Neon magenta (#ff0080) for danger
- Neon lime (#39ff14) for success
- Glassmorphism cards with neon borders

PAGES:
1. Companies - List all connected companies
2. Add Company (OAuth2 flow)

Start with Companies page showing table with name, email, status.
```

---

## 📋 STEG 4: OAuth2 "Connect Microsoft 365" Flow

### Prompt för OAuth2-knapp

```
Add "Connect Microsoft 365" button to Companies page.

On click, it should:
1. Create popup window
2. Navigate to: https://login.microsoftonline.com/common/oauth2/v2.0/authorize with params:
   - client_id: from VITE_AZURE_CLIENT_ID
   - response_type: code
   - redirect_uri: VITE_AZURE_REDIRECT_URI
   - scope: https://outlook.office365.com/IMAP.AccessAsUser.All https://outlook.office365.com/SMTP.Send offline_access
   - response_mode: query
   - state: random generated string

3. When redirected back with authorization code:
   - Exchange code for tokens using Supabase Edge Function
   - Save tokens to Supabase mail_configs table
   - Close popup
   - Refresh companies list

Button should have neon cyan glow and Microsoft logo.
OAuth2 popup should be 500x600px centered.
```

---

## 📋 STEG 5: Supabase Edge Function (Token Exchange)

Skapa Edge Function för att byta authorization code mot tokens:

### `supabase/functions/oauth-exchange/index.ts`

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const AZURE_CLIENT_ID = Deno.env.get('AZURE_CLIENT_ID')!
const AZURE_CLIENT_SECRET = Deno.env.get('AZURE_CLIENT_SECRET')!
const AZURE_TENANT_ID = Deno.env.get('AZURE_TENANT_ID') || 'common'
const TOKEN_URL = `https://login.microsoftonline.com/${AZURE_TENANT_ID}/oauth2/v2.0/token`

serve(async (req) => {
  const { code, companyName, companyEmail } = await req.json()
  
  // Exchange code for tokens
  const tokenResponse = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: AZURE_CLIENT_ID,
      client_secret: AZURE_CLIENT_SECRET,
      code: code,
      grant_type: 'authorization_code',
      redirect_uri: Deno.env.get('AZURE_REDIRECT_URI')!,
      scope: 'https://outlook.office365.com/IMAP.AccessAsUser.All https://outlook.office365.com/SMTP.Send offline_access'
    })
  })
  
  const tokens = await tokenResponse.json()
  
  if (!tokens.access_token) {
    return new Response(JSON.stringify({ error: 'Token exchange failed' }), 
      { status: 400 })
  }
  
  // Get user email from Microsoft Graph
  const graphResponse = await fetch('https://graph.microsoft.com/v1.0/me', {
    headers: { 'Authorization': `Bearer ${tokens.access_token}` }
  })
  const userInfo = await graphResponse.json()
  
  // Calculate token expiry
  const expiresAt = new Date(Date.now() + tokens.expires_in * 1000).toISOString()
  
  // Save to Supabase
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )
  
  // Insert company
  const { data: company, error: companyError } = await supabase
    .from('companies')
    .insert({ 
      name: companyName || userInfo.displayName,
      email: companyEmail || userInfo.mail,
      status: 'active'
    })
    .select()
    .single()
  
  if (companyError) throw companyError
  
  // Insert mail config with OAuth tokens
  await supabase.from('mail_configs').insert({
    company_id: company.id,
    imap_host: 'outlook.office365.com',
    imap_port: 993,
    smtp_host: 'smtp.office365.com',
    smtp_port: 587,
    email_address: userInfo.mail,
    oauth_provider: 'azure',
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token,
    token_expires_at: expiresAt
  })
  
  // Insert default AI config
  await supabase.from('ai_configs').insert({
    company_id: company.id,
    provider: 'openai',
    model: 'gpt-3.5-turbo',
    prompt_template: `Du är en hjälpsam AI-assistent för ${company.name}. Svara professionellt på kundfrågor.`,
    signature: `Med vänliga hälsningar,\n${company.name} Support Team`,
    check_interval: 60,
    max_messages_per_check: 10,
    create_drafts: true,
    auto_send: false
  })
  
  return new Response(
    JSON.stringify({ success: true, company }),
    { headers: { 'Content-Type': 'application/json' } }
  )
})
```

Deploy Edge Function:
```bash
supabase functions deploy oauth-exchange
```

---

## 📋 STEG 6: Lovable React Component

### OAuth2 Button Component

```tsx
import { useState } from 'react'
import { supabase } from '@/lib/supabase'

export function ConnectMicrosoft365() {
  const [loading, setLoading] = useState(false)
  
  const handleConnect = async () => {
    setLoading(true)
    
    // Generate random state for CSRF protection
    const state = crypto.randomUUID()
    sessionStorage.setItem('oauth_state', state)
    
    // Build OAuth2 URL
    const params = new URLSearchParams({
      client_id: import.meta.env.VITE_AZURE_CLIENT_ID,
      response_type: 'code',
      redirect_uri: import.meta.env.VITE_AZURE_REDIRECT_URI,
      response_mode: 'query',
      scope: 'https://outlook.office365.com/IMAP.AccessAsUser.All https://outlook.office365.com/SMTP.Send offline_access openid profile email',
      state: state
    })
    
    const authUrl = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?${params}`
    
    // Open popup
    const popup = window.open(
      authUrl,
      'oauth_popup',
      'width=500,height=600,left=400,top=100'
    )
    
    // Listen for redirect
    const checkPopup = setInterval(() => {
      try {
        if (popup?.closed) {
          clearInterval(checkPopup)
          setLoading(false)
          return
        }
        
        const popupUrl = popup?.location.href
        if (popupUrl?.includes('code=')) {
          const code = new URL(popupUrl).searchParams.get('code')
          const returnedState = new URL(popupUrl).searchParams.get('state')
          
          if (returnedState !== sessionStorage.getItem('oauth_state')) {
            alert('Invalid state - possible CSRF attack')
            popup?.close()
            return
          }
          
          popup?.close()
          clearInterval(checkPopup)
          
          // Exchange code for tokens
          handleTokenExchange(code)
        }
      } catch (e) {
        // Cross-origin error before redirect - ignore
      }
    }, 500)
  }
  
  const handleTokenExchange = async (code: string) => {
    try {
      // Call Supabase Edge Function
      const { data, error } = await supabase.functions.invoke('oauth-exchange', {
        body: { code }
      })
      
      if (error) throw error
      
      alert('✓ Microsoft 365 connected successfully!')
      window.location.reload()
      
    } catch (error) {
      console.error('Token exchange failed:', error)
      alert('Failed to connect Microsoft 365')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <button
      onClick={handleConnect}
      disabled={loading}
      className="
        px-6 py-3 
        bg-neon-cyan/20 
        border-2 border-neon-cyan 
        text-neon-cyan 
        rounded-lg 
        hover:shadow-neon-cyan 
        transition-all 
        disabled:opacity-50
        flex items-center gap-2
      "
    >
      <svg /* Microsoft logo */ />
      {loading ? 'Connecting...' : 'Connect Microsoft 365'}
    </button>
  )
}
```

---

## 🧪 TESTNING

### Flöde:
1. Klicka "Connect Microsoft 365"
2. Popup öppnas med Microsoft login
3. Logga in med Microsoft 365-konto
4. Godkänn permissions
5. Redirect → tokens byts → sparas i Supabase
6. Företag visas i Companies-listan!

### Verifiera i Supabase:
```sql
SELECT 
  c.name,
  c.email,
  mc.oauth_provider,
  mc.token_expires_at
FROM companies c
JOIN mail_configs mc ON mc.company_id = c.id
WHERE mc.oauth_provider = 'azure';
```

---

## 🔐 Säkerhet

- ✅ Client Secret finns ENDAST i Supabase Edge Function (backend)
- ✅ Aldrig i frontend
- ✅ CSRF protection med state parameter
- ✅ Tokens encrypted in transit (HTTPS)
- ✅ Row Level Security i Supabase

---

## 📚 Nästa Steg

Efter att företag är anslutet via OAuth2:
1. Railway backend använder automatiskt OAuth2 tokens
2. Tokens refresh automatiskt (oauth_handler.py)
3. IMAP IDLE startar för företaget
4. Emails processas i realtid!

**Professionell, säker, skalbar! 🚀**
