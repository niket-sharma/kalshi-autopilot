"""Quick test to verify Gemini API key works."""
import google.generativeai as genai
import sys

print("=" * 60)
print("Testing Gemini API Connection")
print("=" * 60)

# Try to get API key from .env
try:
    from dotenv import load_dotenv
    import os
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_gemini_key_here":
        print("\n❌ ERROR: GEMINI_API_KEY not set in .env file")
        print("\n📝 To fix this:")
        print("1. Get your free API key: https://aistudio.google.com/apikey")
        print("2. Edit .env file and replace 'your_gemini_key_here' with your key")
        print("3. Run this test again\n")
        sys.exit(1)
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print(f"\n✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    print("\n🔄 Testing API call...")
    
    # Simple test
    response = model.generate_content("What is 2+2? Answer in one word.")
    result = response.text.strip()
    
    print(f"✅ API call successful!")
    print(f"📊 Response: {result}")
    
    # Test with analysis prompt
    print("\n🔄 Testing market analysis prompt...")
    
    test_prompt = """Analyze this prediction market:

Question: Will Bitcoin hit $100,000 by end of 2026?
Current Market Price: 0.65 (65% probability)

Format your response as:
PROBABILITY: 0.XX
CONFIDENCE: 0.XX
REASONING: Brief explanation
"""
    
    response = model.generate_content(test_prompt)
    print(f"\n✅ Analysis test successful!")
    print(f"📊 Response:\n{response.text}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n🚀 Your bot is ready to use Gemini!")
    print("💰 Cost: FREE (1,500 calls/day)")
    print("\n📝 Next step: Run 'python test_system.py' to test full system\n")
    
except ImportError as e:
    print(f"\n❌ ERROR: Missing dependency: {e}")
    print("\n📝 To fix: pip install google-generativeai python-dotenv")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n📝 Check your GEMINI_API_KEY in .env file")
    print("Get a free key: https://aistudio.google.com/apikey\n")
    sys.exit(1)
