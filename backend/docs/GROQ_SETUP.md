# 🚀 Getting Your Groq API Key

Groq provides fast, free AI inference with generous rate limits - perfect for our bill scanning feature!

## Step 1: Create a Groq Account

1. Go to **https://console.groq.com/**
2. Click **"Sign Up"** or **"Get Started"**
3. Sign up with:
   - Google account
   - GitHub account
   - Or email

## Step 2: Get Your API Key

1. After logging in, you'll be on the Groq Console dashboard
2. Click on **"API Keys"** in the left sidebar
3. Click **"Create API Key"**
4. Give it a name (e.g., "SnapSplit Development")
5. Click **"Create"**
6. **Copy the API key** (you won't be able to see it again!)

## Step 3: Add to Your .env File

1. Open `backend/.env`
2. Find the line: `GROQ_API_KEY=your_groq_api_key_here`
3. Replace `your_groq_api_key_here` with your actual API key
4. Save the file

Example:
```
GROQ_API_KEY=gsk_abc123xyz456...
```

## Step 4: Restart the Server

```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

## ✅ You're Done!

The bill scanning feature will now use Groq instead of Gemini.

## Why Groq?

- ⚡ **Much Faster** - 10-100x faster than other APIs
- 🎯 **Better Rate Limits** - More generous free tier
- 💰 **Free Tier** - Sufficient for development and testing
- 🔧 **JSON Mode** - Native support for structured output

## Models Available

SnapSplit uses **llama-3.1-70b-versatile** which is:
- Fast and accurate
- Great for JSON extraction
- Handles complex receipts well

## Troubleshooting

### "GROQ_API_KEY environment variable not set"
- Make sure you added the key to `.env`
- Restart the server after updating `.env`

### "API call failed: Unauthorized"
- Check that your API key is correct
- Make sure there are no extra spaces
- Verify the key hasn't been revoked

### Rate Limits
Free tier limits (as of 2024):
- 30 requests per minute
- 14,400 requests per day
- More than enough for development!

## Need Help?

- **Groq Documentation**: https://console.groq.com/docs
- **API Reference**: https://console.groq.com/docs/api-reference
- **Community**: https://discord.gg/groq
