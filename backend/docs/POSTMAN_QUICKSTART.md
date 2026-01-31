# Quick Start: Testing SnapSplit API with Postman

## 🚀 Quick Setup (5 minutes)

### 1. Download & Install Postman
- Go to: https://www.postman.com/downloads/
- Download for Windows
- Install and open Postman

### 2. Import the Collection
1. In Postman, click **Import** (top left corner)
2. Click **Upload Files**
3. Navigate to: `C:\Users\krish\Documents\Project\SnapSplit\`
4. Select: `SnapSplit_API.postman_collection.json`
5. Click **Open** → **Import**

You'll see "SnapSplit API" collection in the left sidebar!

### 3. Create Environment
1. Click **Environments** icon (left sidebar, looks like an eye)
2. Click **+** (Create Environment)
3. Name it: `SnapSplit Local`
4. Add ONE variable to start:
   - Variable: `base_url`
   - Initial Value: `http://localhost:8000/api/v1`
   - Current Value: `http://localhost:8000/api/v1`
5. Click **Save**
6. Select "SnapSplit Local" from dropdown (top right corner)

### 4. Make Sure Server is Running
Your server should already be running. Check the terminal:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If not running:
```bash
cd backend
python -m uvicorn main:app --reload
```

## 🧪 Your First Test (2 minutes)

### Test 1: Health Check
1. In left sidebar, expand **SnapSplit API** → **System**
2. Click **Health Check**
3. Click big blue **Send** button
4. You should see in the bottom panel:
   ```json
   {
     "status": "healthy"
   }
   ```
   ✅ Success! Your API is working!

### Test 2: Register a User
1. Expand **Authentication** folder
2. Click **Register User 1 (Alice)**
3. Look at the **Body** tab (below the URL)
4. You'll see:
   ```json
   {
     "email": "alice@example.com",
     "name": "Alice",
     "password": "password123"
   }
   ```
5. Click **Send**
6. You should see response with status **201 Created**:
   ```json
   {
     "email": "alice@example.com",
     "name": "Alice",
     "id": "some-long-uuid-here",
     "created_at": "2024-01-30T..."
   }
   ```
7. **IMPORTANT:** Copy the `id` value (the long UUID)
8. Click **Environments** (top right) → Click **SnapSplit Local**
9. Add new variable:
   - Variable: `user1_id`
   - Value: (paste the UUID you copied)
10. Click **Save**

### Test 3: Login
1. Click **Login User 1 (Alice)**
2. Click **Send**
3. You should see:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```
4. **IMPORTANT:** Copy the entire `access_token` value
5. Go to Environments → Add new variable:
   - Variable: `token`
   - Value: (paste the token)
6. Click **Save**

✅ You're now authenticated! All other requests will use this token automatically.

## 📋 Complete Testing Flow

Now follow this order (each request builds on the previous):

### Authentication (Already Done ✅)
- [x] Register User 1 (Alice)
- [x] Login User 1 (Alice)
- [ ] Register User 2 (Bob)
- [ ] Login User 2 (Bob)

### Friends
- [ ] Send Friend Request (Alice → Bob)
- [ ] Accept Friend Request (Bob accepts) - **Switch to Bob's token!**
- [ ] Get Friends List

### Groups
- [ ] Create Group
- [ ] Add Member to Group
- [ ] Get Groups List
- [ ] Get Group Details

### Expenses
- [ ] Create Manual Expense
- [ ] Get Expense Details
- [ ] Get Group Expenses

### Settlements
- [ ] Get Group Balances (before settlement)
- [ ] Create Settlement (Bob pays Alice) - **Use Bob's token!**
- [ ] Get Updated Balances (after settlement)

## 💡 Key Tips

### When to Switch Tokens
Some requests need Bob's token instead of Alice's:
1. **Accept Friend Request** - Bob is accepting
2. **Create Settlement** - Bob is paying

To switch:
1. Go to **Authorization** tab in the request
2. Change `{{token}}` to `{{token_bob}}`

### Copying IDs from Responses
After each request that creates something:
1. Find the `id` in the response
2. Copy it
3. Save it in the environment:
   - `user2_id` - Bob's user ID
   - `request_id` - Friend request ID
   - `group_id` - Group ID
   - `expense_id` - Expense ID

### Understanding the Response
- **Green status (200, 201)** = Success! ✅
- **Red status (400, 401, 403, 404)** = Error ❌
- Read the `detail` field in error responses for explanation

### Using Variables
Variables use `{{variable_name}}` syntax:
- `{{base_url}}` - API base URL
- `{{token}}` - Your JWT token
- `{{user1_id}}` - Alice's ID
- `{{user2_id}}` - Bob's ID
- `{{group_id}}` - Current group ID

## 🎯 What to Expect

### After Creating Expense ($60 split equally)
Balances should show:
- Alice: +$30 (she paid $60, owes $30)
- Bob: -$30 (he owes $30)

### After Bob Pays $15
Balances should update:
- Alice: +$45 (was +$30, received $15)
- Bob: -$15 (was -$30, paid $15)

## ❓ Troubleshooting

### "401 Unauthorized"
- Your token expired or is invalid
- Login again and update the `token` variable

### "403 Forbidden"
- You don't have permission
- Check if you're using the right user's token
- Check if user is a group member

### "404 Not Found"
- The ID doesn't exist
- Check your environment variables are set correctly
- Make sure you copied the IDs from previous responses

### "400 Bad Request"
- Invalid input data
- Read the error message in the response
- Check the request body matches the expected format

## 🎉 Success Criteria

You've successfully tested the API when:
- ✅ Two users registered and logged in
- ✅ Friend request sent and accepted
- ✅ DIRECT group created automatically
- ✅ Regular group created with members
- ✅ Expense created and split calculated
- ✅ Balances show correct amounts
- ✅ Settlement created and balances updated

## 📚 Next Steps

After manual testing:
1. Try creating more users and groups
2. Test error cases (invalid data, wrong permissions)
3. Use Postman's **Collection Runner** to automate tests
4. Export your environment to save your progress

---

**Need Help?** Check the full guide: `backend/docs/POSTMAN_GUIDE.md`
