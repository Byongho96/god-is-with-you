import os
import json
from datetime import date
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from google import genai
from google.genai import types

from server.schemas import VerseRequest, VerseResponse

# ---------------------------------------------------------
# Configuration & Initialization
# ---------------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = 'gemini-2.5-flash'

app = FastAPI(
    title="Bible Verse & Comfort API",
    description="Provides daily random verses and situational custom messages.",
    version="1.1.0"
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://byongho96.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Cache Memory (Only for Daily Verses)
# ---------------------------------------------------------
DAILY_VERSE_CACHE = {}

def get_daily_cache_key(language: str) -> str:
    """Generates a cache key based on the current date and language."""
    today_str = date.today().isoformat()
    return f"{today_str}_{language.lower()}"


def get_name_context_and_instruction(name: str | None, language: str) -> tuple[str, str]:
    """Builds prompt context/instruction for name-based listener replacement."""
    if name and name.strip():
        normalized_name = name.strip()
        return (
            f"User's Name: {normalized_name}",
            (
                "If the verse listener is expressed as words like 'Israel', 'Jacob', 'you', or equivalent second-person/listener nouns, "
                f"replace only that listener target with '{normalized_name}'. "
                f"Adjust particles/prepositions/case markers to be grammatically natural in {language}. "
                "Do not paraphrase the sentence and do not change the theological meaning."
            ),
        )

    return (
        "No name provided.",
        "Do not replace listener targets. Preserve the original verse wording in the target language.",
    )

# ---------------------------------------------------------
# Helper Function for Gemini API Calls
# ---------------------------------------------------------
async def fetch_from_gemini(prompt: str, temperature: float = 0.9) -> dict:
    try:
        response = await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json"
            )
        )
        
        raw_text = response.text.strip()
        
        # Handle cases where Gemini wraps JSON in code blocks
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
            
        return json.loads(raw_text)
    except Exception as e:
        print(f"[Error] Gemini API failure: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate content.")

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "date": date.today().isoformat()}

@app.get("/api/v1/daily-verse", response_model=VerseResponse, tags=["Verse"])
async def generate_daily_verse(
    language: str = Query("Korean", description="Target language for the verse")
):
    """
    Returns a highly random, uplifting Bible verse to start the day.
    Caches the result for 24 hours based on the requested language.
    """
    cache_key = get_daily_cache_key(language)
    
    # 1. Check Cache
    if cache_key in DAILY_VERSE_CACHE:
        return DAILY_VERSE_CACHE[cache_key]
    
    # 2. Prompt for High Randomness (Temperature will be 1.0)
    prompt = f"""
    Target Language: {language}

    Instructions:
    1. Select a highly uplifting, encouraging, and positive Bible verse perfect for starting the day.
    2. CRITICAL FOR RANDOMNESS: To ensure a fresh experience every day, AVOID the top 50 most commonly quoted verses (e.g., John 3:16, Philippians 4:13, Jeremiah 29:11). 
    3. Dig deep into the Wisdom literature (Proverbs, Ecclesiastes), Minor Prophets, or lesser-known Epistles to find a hidden gem.
    4. Return the verse text in {language} using canonical Scripture wording as-is. No paraphrase, no conversational tone, and no additional commentary.
    5. Verify the reference is a real, existing Bible passage (valid book/chapter/verse). If uncertain, choose a different verse you can verify.
    6. Output STRICTLY in JSON format with exactly two keys: "verse" (the text) and "ref" (the citation).
    
    Expected JSON Output:
    {{
        "verse": "...",
        "ref": "..."
    }}
    """
    
    # Use max temperature for maximum variety
    parsed_data = await fetch_from_gemini(prompt, temperature=1.0)
    result = VerseResponse(**parsed_data)
    
    # 3. Save to Cache
    DAILY_VERSE_CACHE[cache_key] = result
    return result

@app.post("/api/v1/custom-message", response_model=VerseResponse, tags=["Message"])
async def generate_custom_message(
    request: VerseRequest | None = None,
    name: str | None = Query(None, description="Optional user name to inject for listener references."),
    language: str = Query("Korean", description="Target language for the verse")
):
    """
    Generates a personalized, situational message based on a Bible verse.
    This endpoint does NOT use caching and generates a fresh response every time.
    """

    # Situation-based instructions
    if request and request.situation:
        sit_context = f"User's Current Situation: {request.situation}"
        sit_instruction = "Select a comforting or guiding Bible verse that directly addresses the user's situation."
    else:
        sit_context = "No specific situation provided."
        sit_instruction = "Since no situation is provided, select a highly encouraging, powerful, and random Bible verse."

    name_context, name_instruction = get_name_context_and_instruction(name, language)

    prompt = f"""
    Context:
    - {name_context}
    - {sit_context}
    - Target Language: {language}

    Instructions:
    1. {sit_instruction}
    2. If the situation is nonsensical (e.g., 'asdf'), select a random powerful verse.
    3. {name_instruction}
    4. Return the verse text in {language} using canonical Scripture wording as-is. No paraphrase, no conversational tone, and no additional commentary.
    5. If a name replacement is applied, adjust only grammar markers (particles/prepositions/case markers) minimally for naturalness in {language}.
    6. Verify the reference is a real, existing Bible passage (valid book/chapter/verse). If uncertain, choose a different verse you can verify.
    7. Output STRICTLY in JSON format with exactly two keys: "verse" (the text) and "ref" (the citation).
    """
    
    # Use slightly lower temperature for more coherent situational matching
    parsed_data = await fetch_from_gemini(prompt, temperature=0.8)
    return VerseResponse(**parsed_data)