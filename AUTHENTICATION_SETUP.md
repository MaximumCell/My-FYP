# Authentication Setup - PhysicsLab

## Overview

PhysicsLab uses **Clerk** for secure authentication with support for:

- ✅ Email/password sign-up and sign-in
- ✅ OAuth (Google, GitHub, Microsoft, etc.)
- ✅ Email verification
- ✅ Password recovery
- ✅ User profile management

## Created Pages

### 1. **Sign-Up Page** (`/auth/sign-up`)

- Beautiful, modern design with gradient background
- Clerk sign-up form with custom styling
- Features list showing PhysicsLab benefits
- Link to sign-in page for existing users
- Responsive design (mobile-friendly)

**Features:**

- Email and password signup
- Social OAuth options
- Form validation
- Automatic redirect to `/ai` after signup

### 2. **Sign-In Page** (`/auth/sign-in`)

- Professional login interface
- Clerk sign-in form with matching design
- Quick access links to AI Tutor and Simulations
- Security information badge
- Password recovery support

**Features:**

- Email/password login
- Social OAuth options
- "Forgot password?" support
- Link to create new account
- Automatic redirect to `/ai` after login

### 3. **Auth Layout** (`/auth/layout.tsx`)

- Shared layout for all auth pages
- Consistent gradient background
- Metadata configuration

## Configuration

### Environment Variables Required

Add these to your `.env.local` file:

```bash
# Clerk Configuration
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key

# Optional: Clerk Redirect URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/auth/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/auth/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/ai
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/ai
```

### How to Get Clerk API Keys

1. Go to [clerk.com](https://clerk.com)
2. Sign up for a free account
3. Create a new application
4. Navigate to API Keys section
5. Copy the **Publishable Key** and **Secret Key**
6. Add them to your `.env.local` file

## Usage

### For Users

1. **Sign Up:**

   - Visit `/auth/sign-up`
   - Enter email and password OR use OAuth
   - Verify email (if required)
   - Redirected to `/ai` automatically

2. **Sign In:**

   - Visit `/auth/sign-in`
   - Enter credentials OR use OAuth
   - Redirected to `/ai` automatically

3. **Sign Out:**
   - Click user avatar in header
   - Select "Sign out"

### For Developers

#### Protected Routes

Routes that require authentication:

- `/ai` - AI Tutor (must be signed in)
- `/ml` - ML Lab (must be signed in)
- `/simulation` - Physics Simulations (must be signed in)

Public routes:

- `/` - Home page
- `/docs` - Documentation
- `/auth/sign-in` - Sign-in page
- `/auth/sign-up` - Sign-up page

#### Protecting Routes

To protect a route, you can use:

```typescript
// Method 1: Use Clerk middleware (automatic via config)
// All protected routes are handled by middleware

// Method 2: Use Clerk hooks in components
import { useAuth } from "@clerk/nextjs";

export default function ProtectedComponent() {
  const { isSignedIn, userId } = useAuth();

  if (!isSignedIn) {
    return <div>Please sign in</div>;
  }

  return <div>Protected content for user {userId}</div>;
}
```

#### Getting User Information

```typescript
import { currentUser } from "@clerk/nextjs/server";

export default async function UserProfile() {
  const user = await currentUser();

  return (
    <div>
      <h1>
        Welcome, {user?.firstName || user?.emailAddresses[0].emailAddress}
      </h1>
    </div>
  );
}
```

## Styling

The authentication pages use:

- **Color Scheme:** Dark theme (slate-800, slate-900)
- **Gradients:** Blue to Cyan gradient
- **Components:** Tailwind CSS with custom Clerk styling
- **Responsive:** Mobile-first design

### Customizing Colors

Edit the color classes in the sign-up/sign-in pages:

```tsx
// Example: Change primary gradient
className = "from-blue-400 to-cyan-400"; // Current
// Change to:
className = "from-purple-400 to-pink-400"; // Custom
```

## API Routes

### User Authentication

Clerk handles all authentication automatically. The system uses:

1. **Client-side:** Clerk components in pages
2. **Server-side:** Clerk middleware for protection
3. **API routes:** Automatic Clerk protection via middleware

### Example API Call with Authentication

```typescript
// frontend/src/lib/physics-api.ts
import { auth } from "@clerk/nextjs/server";

export const askPhysicsQuestion = async (question: string) => {
  const { userId } = await auth();

  const response = await fetch("/api/physics/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${userId}`,
    },
    body: JSON.stringify({ question }),
  });

  return response.json();
};
```

## Database Integration

To store user data:

1. **User ID:** Available from `currentUser()` or `useAuth()`
2. **User Email:** From `user.emailAddresses[0].emailAddress`
3. **User Name:** From `user.firstName`, `user.lastName`

Example:

```typescript
const user = await currentUser();
const userData = {
  clerkId: user.id,
  email: user.emailAddresses[0].emailAddress,
  name: `${user.firstName} ${user.lastName}`,
  createdAt: new Date(),
};
```

## Security Best Practices

✅ **Implemented:**

- Sessions are secure and HttpOnly
- User data is encrypted in transit
- OAuth tokens are securely stored
- Rate limiting on authentication endpoints
- Email verification on signup

✅ **Recommended:**

- Always validate user input
- Use HTTPS in production
- Keep environment variables secret
- Implement CSRF protection
- Log authentication events

## Troubleshooting

### Issue: "Clerk API key missing"

**Solution:**

- Check `.env.local` has `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- Restart the development server
- Verify keys are correct from Clerk dashboard

### Issue: "Redirect loop after sign-in"

**Solution:**

- Check environment variables
- Verify `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/ai` is set
- Ensure `/ai` route exists and is accessible

### Issue: "OAuth not working"

**Solution:**

- Configure OAuth provider in Clerk dashboard
- Set correct redirect URIs in OAuth provider settings
- Verify domain is whitelisted in Clerk

## File Structure

```
frontend/src/
├── app/
│   ├── auth/
│   │   ├── layout.tsx ................. Auth pages layout
│   │   ├── sign-in/
│   │   │   └── page.tsx .............. Sign-in page
│   │   └── sign-up/
│   │       └── page.tsx .............. Sign-up page
│   ├── layout.tsx .................... Root layout (ClerkProvider)
│   └── ...
├── middleware.ts .................... Clerk middleware
├── components/
│   └── header.tsx ................... Auth buttons in header
└── ...
```

## Testing Authentication

### Test Sign-Up Flow

1. Navigate to `http://localhost:3000/auth/sign-up`
2. Enter test email and password
3. Should redirect to `/ai`
4. Check user avatar appears in header

### Test Sign-In Flow

1. Sign out (click avatar → Sign out)
2. Navigate to `http://localhost:3000/auth/sign-in`
3. Enter credentials
4. Should redirect to `/ai`

### Test Protected Routes

1. Sign out
2. Try to access `/ai`
3. Should redirect to `/auth/sign-in`

## Next Steps

1. ✅ Set up Clerk account and get API keys
2. ✅ Add environment variables to `.env.local`
3. ✅ Test sign-up flow at `/auth/sign-up`
4. ✅ Test sign-in flow at `/auth/sign-in`
5. ✅ Configure OAuth providers (optional)
6. ✅ Deploy to production

## Additional Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk Next.js Integration](https://clerk.com/docs/quickstarts/nextjs)
- [OAuth Setup Guide](https://clerk.com/docs/social-providers)
- [User Management](https://clerk.com/docs/users)

## Support

If you encounter issues:

1. Check [Clerk documentation](https://clerk.com/docs)
2. Review environment variables
3. Check browser console for errors
4. Check server logs for backend errors
5. Verify API keys are correct

---

**Status:** ✅ Authentication pages created and ready to use
**Date:** October 23, 2025
**Type:** Clerk Integration
