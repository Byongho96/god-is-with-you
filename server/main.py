import os
import random
from datetime import date, datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from google import genai
from google.genai import types

from server.constants import (
    CANONICAL_LANGUAGE_NAMES,
    LANGUAGE_ALIASES,
    PREDEFINED_DAILY_VERSES,
    UNAUTHORIZED_MESSAGES,
)
from server.schemas import VerseRequest, VerseResponse

# ---------------------------------------------------------
# Configuration & Initialization
# ---------------------------------------------------------
load_dotenv()

KST = timezone(timedelta(hours=9))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = 'gemini-2.5-flash-lite'

# Allowed NFC keys for simple API key-based access control (comma-separated in .env)
ALLOWED_NFC_KEYS = {
    key.strip() for key in os.getenv("ALLOWED_NFC_KEYS", "").split(",") if key.strip()
}

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

SYSTEM_INSTRUCTION = """
Role: Bible Verse API.
Rules:
1. Exact canonical Scripture only. No paraphrase, no commentary.
2. Real passages only. No hallucinations.
3. Output strictly in requested language.
4. JSON format only (keys: verse, ref). No markdown tags.
"""
def get_seconds_until_midnight():
    now = datetime.now(KST)  # 현재 한국 시간
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((tomorrow - now).total_seconds())


def normalize_language(language: str | None) -> str:
    """Normalizes incoming language values to a supported canonical language name."""
    normalized_value = (language or "Korean").strip().lower()

    for language_key, aliases in LANGUAGE_ALIASES.items():
        if normalized_value in aliases:
            return CANONICAL_LANGUAGE_NAMES[language_key]

    return "Korean"


def get_language_key(language: str | None) -> str:
    return normalize_language(language).lower()


def is_authorized_nfc_key(key: str | None) -> bool:
    if not key:
        return False

    return key.strip() in ALLOWED_NFC_KEYS


def get_predefined_daily_verse(language: str | None) -> VerseResponse:
    language_key = get_language_key(language)
    return VerseResponse(**PREDEFINED_DAILY_VERSES[language_key])


def get_unauthorized_response(language: str | None) -> VerseResponse:
    language_key = get_language_key(language)
    return VerseResponse(**UNAUTHORIZED_MESSAGES[language_key])


def get_name_context_and_instruction(name: str | None, language: str) -> tuple[str, str]:
    """Builds highly minified prompt context/instruction for name replacement."""
    if name and name.strip():
        normalized_name = name.strip()
        return (
            f"Name: {normalized_name}",
            f"Replace listener nouns (e.g., 'you', 'Israel', 'Jacob') with '{normalized_name}'. Adjust {language} grammar naturally."
        )

    return (
        "Name: None",
        "Keep original listener names."
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
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=temperature,
                response_mime_type="application/json",
                response_schema=VerseResponse # Pydantic model for automatic parsing and validation
            )
        )
        
        return response.parsed.model_dump() 
        
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
    response: Response,
    language: str = Query("Korean", description="Target language for the verse"),
    key: str | None = Query(None, description="NFC key for access control")
):
    """
    Returns a highly random, uplifting Bible verse to start the day.
    Caches the result for 24 hours based on the requested language.
    """
    # Set Cache Configuration
    seconds_left = get_seconds_until_midnight()
    
    cache_time = max(seconds_left, 60)
    response.headers["Cache-Control"] = f"public, s-maxage={cache_time}, stale-while-revalidate=60"
    
    normalized_language = normalize_language(language)

    if not is_authorized_nfc_key(key):
        return get_predefined_daily_verse(normalized_language)

    # Simple randomization for verse selection strategy (5% chance for famous, 95% for lesser-known)
    if random.random() < 0.05:
        rule_text = "Select a highly famous, beloved classic verse (e.g., Psalms, Gospels) that everyone loves."
    else:
        rule_text = "AVOID top 50 common verses (e.g., John 3:16). Use lesser-known books (Wisdom, Minor Prophets)."

    prompt = f"""
    Lang: {normalized_language}
    Task: Uplifting morning verse.
    Rule: {rule_text}
    """

    # 2. Use max temperature for maximum variety
    parsed_data = await fetch_from_gemini(prompt, temperature=0.9)
    result = VerseResponse(**parsed_data)
    
    return result

@app.post("/api/v1/custom-message", response_model=VerseResponse, tags=["Message"])
async def generate_custom_message(
    request: VerseRequest | None = None,
    name: str | None = Query(None, description="Optional user name to inject for listener references."),
    language: str = Query("Korean", description="Target language for the verse"),
    key: str | None = Query(None, description="NFC key for access control")
):
    """
    Generates a personalized, situational message based on a Bible verse.
    This endpoint does NOT use caching and generates a fresh response every time.
    """
    normalized_language = normalize_language(language)

    if not is_authorized_nfc_key(key):
        return get_unauthorized_response(normalized_language)

    # Situation-based instructions
    if request and request.situation:
        sit_context = f"Situation: {request.situation}"
        sit_instruction = "Address situation directly. If nonsense, give general encouragement."
    else:
        sit_context = "Situation: None"
        sit_instruction = "General powerful encouragement."

    name_context, name_instruction = get_name_context_and_instruction(name, normalized_language)

    prompt = f"""
    Lang: {normalized_language}
    {sit_context}
    {name_context}
    
    Task:
    1. {sit_instruction}
    2. {name_instruction}
    """
    
    # Use slightly lower temperature for more coherent situational matching
    parsed_data = await fetch_from_gemini(prompt, temperature=0.8)
    return VerseResponse(**parsed_data)
