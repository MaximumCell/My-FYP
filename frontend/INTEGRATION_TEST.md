# Frontend-Backend Integration Test Guide

## 🚀 How to Test User Sync Integration

### Prerequisites:

1. Backend Flask app running on `http://localhost:5000`
2. Frontend Next.js app running (usually on `http://localhost:3000`)
3. MongoDB Atlas connection working
4. Clerk authentication configured

### Testing Steps:

1. **Start Backend Server:**

   ```bash
   cd backend
   python app.py
   ```

   Should see: `Database initialized successfully`

2. **Start Frontend Server:**

   ```bash
   cd frontend2
   npm run dev
   ```

3. **Test the Integration:**

   - Open `http://localhost:3000`
   - Click "Sign Up" or "Sign In"
   - Create a new account or sign in with existing account
   - After successful authentication, you should see:
     - ✅ "Account Synced" message briefly
     - User dashboard with stats (initially zeros)
     - Debug panel in bottom-right (in development mode)

4. **Verify in MongoDB:**
   - Check your MongoDB Atlas cluster
   - You should see the `users` collection
   - Each sign-in should create/update a user document

### What Happens Behind the Scenes:

1. **User signs in with Clerk** → Clerk provides user data
2. **UserProvider automatically syncs** → Calls `/api/users/sync`
3. **Backend creates/updates user** → Stores in MongoDB
4. **Dashboard data loads** → Shows user stats and info
5. **User sees personalized experience** → Dashboard reflects their data

### Debugging:

- **Check browser console** for sync logs
- **Check Flask terminal** for API calls
- **Use debug panel** (bottom-right in development)
- **MongoDB Atlas** should show new users collection

### Expected API Calls:

```
POST /api/users/sync
GET /api/users/dashboard?clerk_user_id=...
GET /health (optional)
```

### Success Indicators:

- ✅ No errors in browser console
- ✅ User document appears in MongoDB
- ✅ Dashboard shows user information
- ✅ Debug panel shows all green checkmarks

### Common Issues:

- **CORS errors**: Make sure Flask CORS is configured
- **Connection refused**: Ensure backend is running on port 5000
- **MongoDB errors**: Check connection string and database access
- **Clerk errors**: Verify API keys in .env.local
