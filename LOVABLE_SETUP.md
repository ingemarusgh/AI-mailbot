# 🚀 LOVABLE FRONTEND SETUP GUIDE

**AI Mailbot Admin Panel - Dark Cyberpunk Theme**

---

## 📋 STEG 1: Skapa Lovable Projekt

### 1.1 Gå till Lovable
1. Öppna [https://lovable.dev](https://lovable.dev)
2. Logga in eller skapa konto

### 1.2 Skapa Nytt Projekt
1. Klicka **"New Project"**
2. Välj **"Blank Project"** eller **"Supabase Starter"**
3. Projekt-namn: `AI Mailbot Admin`

---

## 📋 STEG 2: Konfigurera Supabase Connection

### 2.1 Lägg Till Environment Variables

I Lovable projekt → **Settings** → **Environment Variables**:

```bash
VITE_SUPABASE_URL=https://urauulfqtwfxvwmtsomd.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVyYXV1bGZxdHdmeHZ3bXRzb21kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0NDc2OTQsImV4cCI6MjA4NzAyMzY5NH0.rRpynHFcl52XRJqFRlve4uY0VYnUP7a_fM2QWiXJkok
```

⚠️ **OBS:** Använd `ANON_KEY` (inte service_role!) för frontend

---

## 📋 STEG 3: Prompta Lovable AI

### 3.1 Design Prompt (Kopiera detta till Lovable chat)

```
Create a dark cyberpunk admin dashboard for an AI email bot SaaS platform.

DESIGN THEME:
- Dark background (#0a0a0a, #1a1a1a)
- Neon accent colors:
  * Cyan (#00f5ff) - primary buttons and links
  * Magenta (#ff0080) - delete/danger actions
  * Lime green (#39ff14) - success states
  * Purple (#b026ff) - secondary elements
  * Yellow (#ffed4e) - warnings
- Glassmorphism cards with neon borders
- Modern sans-serif font (Inter or similar)
- Smooth animations and transitions

PAGES TO CREATE:
1. Dashboard - Stats overview with neon charts
2. Companies - CRUD for managing client companies
3. Config Editor - Email and AI settings per company
4. Users - Multi-user management per company
5. Activity Logs - Real-time email processing activity

Use React, TypeScript, Tailwind CSS, and Supabase client.
```

### 3.2 Komponenter att be om (en i taget)

**A) Sidebar Navigation**
```
Create a dark sidebar navigation with neon cyan highlights.
Include icons for: Dashboard, Companies, Users, Logs, Settings.
Active link should have neon glow effect.
```

**B) Companies Table**
```
Create a data table for companies with columns:
- Name, Email, Status (active/inactive badge with neon colors)
- Actions: Edit, Delete (neon magenta), View Stats

Include "Add Company" button with neon cyan glow.
Table should have dark background with subtle neon borders.
```

**C) Add Company Form**
```
Create a modal form for adding companies with fields:
- Company Name, Email
- IMAP/SMTP settings (host, port, credentials)
- AI Prompt Template (textarea)
- Signature (textarea)

Use dark glassmorphism background, neon cyan borders.
Submit button with neon glow effect on hover.
```

**D) Dashboard Stats**
```
Create a dashboard with stat cards showing:
- Total Companies
- Emails Processed Today
- Drafts Created
- Error Rate

Each card: dark background, neon border (different color per stat)
Include a neon line chart showing email volume over time.
```

---

## 📋 STEG 4: Supabase Integration Code

### 4.1 Skapa Supabase Client (`src/lib/supabase.ts`)

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export type Company = {
  id: string
  name: string
  email: string
  status: 'active' | 'inactive' | 'paused'
  created_at: string
  updated_at: string
}

export type MailConfig = {
  id: string
  company_id: string
  imap_host: string
  imap_port: number
  smtp_host: string
  smtp_port: number
  email_address: string
  email_password: string
}

export type AIConfig = {
  id: string
  company_id: string
  provider: string
  model: string
  prompt_template: string
  signature: string
  check_interval: number
  max_messages_per_check: number
  create_drafts: boolean
  auto_send: boolean
}
```

### 4.2 Companies Hook (`src/hooks/useCompanies.ts`)

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase, type Company } from '@/lib/supabase'

export function useCompanies() {
  return useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('companies')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data as Company[]
    }
  })
}

export function useAddCompany() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (company: Omit<Company, 'id' | 'created_at' | 'updated_at'>) => {
      const { data, error } = await supabase
        .from('companies')
        .insert(company)
        .select()
        .single()
      
      if (error) throw error
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    }
  })
}

export function useDeleteCompany() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase
        .from('companies')
        .delete()
        .eq('id', id)
      
      if (error) throw error
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    }
  })
}
```

---

## 📋 STEG 5: Tailwind Config för Neon Theme

Be Lovable lägga till detta i `tailwind.config.js`:

```javascript
export default {
  theme: {
    extend: {
      colors: {
        neon: {
          cyan: '#00f5ff',
          magenta: '#ff0080',
          lime: '#39ff14',
          purple: '#b026ff',
          yellow: '#ffed4e',
        },
        dark: {
          bg: '#0a0a0a',
          card: '#1a1a1a',
          border: '#2a2a2a',
        }
      },
      boxShadow: {
        'neon-cyan': '0 0 20px rgba(0, 245, 255, 0.5)',
        'neon-magenta': '0 0 20px rgba(255, 0, 128, 0.5)',
        'neon-lime': '0 0 20px rgba(57, 255, 20, 0.5)',
      }
    }
  }
}
```

---

## 📋 STEG 6: Exempel-komponenter

### Companies Page (`src/pages/Companies.tsx`)

```tsx
import { useCompanies, useDeleteCompany } from '@/hooks/useCompanies'
import { Button } from '@/components/ui/button'
import { PlusIcon, TrashIcon } from 'lucide-react'

export default function Companies() {
  const { data: companies, isLoading } = useCompanies()
  const deleteCompany = useDeleteCompany()

  if (isLoading) return <div className="text-neon-cyan">Loading...</div>

  return (
    <div className="p-8 bg-dark-bg min-h-screen">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-neon-cyan">Companies</h1>
        <Button className="bg-neon-cyan hover:shadow-neon-cyan">
          <PlusIcon className="mr-2" />
          Add Company
        </Button>
      </div>

      <div className="border border-dark-border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-dark-card border-b border-dark-border">
            <tr>
              <th className="p-4 text-left text-neon-purple">Name</th>
              <th className="p-4 text-left text-neon-purple">Email</th>
              <th className="p-4 text-left text-neon-purple">Status</th>
              <th className="p-4 text-left text-neon-purple">Actions</th>
            </tr>
          </thead>
          <tbody>
            {companies?.map((company) => (
              <tr key={company.id} className="border-b border-dark-border hover:bg-dark-card">
                <td className="p-4 text-white">{company.name}</td>
                <td className="p-4 text-gray-400">{company.email}</td>
                <td className="p-4">
                  <span className={`px-3 py-1 rounded-full text-xs ${
                    company.status === 'active' 
                      ? 'bg-neon-lime/20 text-neon-lime' 
                      : 'bg-neon-magenta/20 text-neon-magenta'
                  }`}>
                    {company.status}
                  </span>
                </td>
                <td className="p-4">
                  <button 
                    onClick={() => deleteCompany.mutate(company.id)}
                    className="text-neon-magenta hover:shadow-neon-magenta"
                  >
                    <TrashIcon size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

---

## 🚀 Nästa Steg

1. **Starta Lovable projekt** med design prompt
2. **Be AI skapa komponenter** en i taget
3. **Integrera Supabase** med kod ovan
4. **Testa live preview** i Lovable
5. **Deploy** när du är nöjd!

---

## 💡 Tips

- Be Lovable AI iterera på designen tills du är nöjd
- Du kan ändra neon-färger när som helst
- Använd Lovable's live preview för att se ändringar direkt
- Komponenter är modulära - lägg till fler funktioner steg för steg

**Lycka till! 🔥**
