# How to Get Your Free Gemini API Key

## Quick Steps (2 minutes)

1. **Go to Google AI Studio**
   - Visit: https://aistudio.google.com/apikey
   - Sign in with your Google account (sharma.niket@gmail.com)

2. **Create API Key**
   - Click "Get API key" or "Create API key"
   - Choose "Create API key in new project" (or use existing)
   - Copy the key (starts with `AIza...`)

3. **Add to .env file**
   ```bash
   cd ~/ai/polymarket-autopilot
   nano .env
   ```
   
   Replace:
   ```
   GEMINI_API_KEY=your_gemini_key_here
   ```
   
   With:
   ```
   GEMINI_API_KEY=AIzaSy...your_actual_key
   ```
   
   Save and exit (Ctrl+X, Y, Enter)

4. **Done!**
   - Free tier: 1,500 requests per day
   - Way more than enough for the trading bot
   - No credit card required

## Alternative: Use Existing Google Auth

You already have Google Gemini CLI configured in OpenClaw, but that uses OAuth (not API key).
The API key is simpler and works the same. Just get it from the link above!

---

**Next:** Once you add the key, run `python test_system.py` to verify everything works!
