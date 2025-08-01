# Clerk + Supabase Integration Setup Guide

This guide will help you set up the integration between Clerk and Supabase using the modern third-party auth approach. This setup uses Clerk for user management and Supabase for your application data.

## Prerequisites

- A Clerk account and application
- A Supabase project
- Next.js application with both `@clerk/nextjs` and `@supabase/supabase-js` installed

## Step 1: Configure Supabase Third-Party Auth

1. Go to your **Supabase Dashboard**
2. Navigate to **Authentication > Integrations**
3. Add a new **Third-Party Auth** integration
4. Select **Clerk** from the list
5. Follow the configuration steps provided by Supabase

## Step 2: Configure Clerk for Supabase

1. Visit **Clerk's Connect with Supabase** page in your Clerk dashboard
2. Follow the setup instructions to configure your Clerk instance for Supabase compatibility
3. This will set up the necessary JWT claims and configuration

## Step 3: Environment Variables

Copy your `.env.example` to `.env.local` and fill in the required values:

```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

## Step 4: Test the Integration

1. Start your Next.js application
2. Sign up/in through Clerk
3. Try making authenticated requests to Supabase

## Usage Examples

### Server-side data fetching:

```typescript
import { createSupabaseServerClient } from '@/lib/supabase'

export async function getData() {
  const supabase = await createSupabaseServerClient()
  
  const { data, error } = await supabase
    .from('your_table')
    .select('*')
  
  return data
}
```

### Client-side usage:

```typescript
import { supabase } from '@/lib/supabase'
import { useAuth } from '@clerk/nextjs'

function MyComponent() {
  const { getToken } = useAuth()

  const fetchData = async () => {
    const token = await getToken()
    
    const { data, error } = await supabase
      .from('your_table')
      .select('*')
      .auth(token)
  }
}
```

### Get current user (from Clerk):

```typescript
import { getCurrentUser } from '@/lib/user'

export async function ProfilePage() {
  const user = await getCurrentUser()
  
  if (!user) {
    redirect('/sign-in')
  }
  
  return <div>Welcome {user.firstName}!</div>
}
```

## Row Level Security (RLS)

Create RLS policies in your Supabase tables that use Clerk user IDs. Example:

```sql
-- Enable RLS on your table
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;

-- Allow users to read their own data
CREATE POLICY "Users can read own data" ON your_table
  FOR SELECT USING (auth.jwt() ->> 'sub' = user_id);

-- Allow users to insert their own data
CREATE POLICY "Users can insert own data" ON your_table
  FOR INSERT WITH CHECK (auth.jwt() ->> 'sub' = user_id);
```

## Troubleshooting

### Authentication errors
- Ensure third-party auth is properly configured in Supabase
- Verify your Supabase URL and keys are correct
- Check that RLS policies allow the operations you're trying to perform

### Token issues
- Make sure you're using `createSupabaseServerClient()` for server-side operations
- For client-side, ensure you're passing the Clerk token to Supabase