# Bible Verse & Comfort API

A FastAPI service that generates Bible verses using Gemini, with optional personalization by `name` and output translation by `language`.

NFC key authorization is enforced through `ALLOWED_NFC_KEYS` in the environment.

## Requirements

- Python 3.11+
- `GEMINI_API_KEY`

## Local Run

1. Install dependencies.

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
ALLOWED_NFC_KEYS=key1,key2,key3
```

3. Start the server.

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. Verify endpoints.

- Health: `http://localhost:8000/health`
- Docs: `http://localhost:8000/docs`

## Docker Run

```bash
docker build -t bible-api .
docker run --rm -p 8000:8000 --env-file .env bible-api
```

## API

### `GET /api/v1/daily-verse`

Query parameters:

- `language` (optional, default: `Korean`)
- `key` (optional, but required for Gemini-generated content)

Behavior:

- If `key` is missing or not included in `ALLOWED_NFC_KEYS`, the API returns a predefined verse.
- English variants such as `EN`, `en`, `English`, and `english` are normalized to English.

Example:

```bash
curl "http://localhost:8000/api/v1/daily-verse?language=Korean&key=YOUR_NFC_KEY"
```

### `POST /api/v1/custom-message`

Query parameters:

- `name` (optional)
- `language` (optional, default: `Korean`)
- `key` (optional, but required for authorized generation)

JSON body:

- `situation` (optional)

Behavior:

- If `key` is missing or not included in `ALLOWED_NFC_KEYS`, the API returns an unauthorized-user message.

Example:

```bash
curl -X POST "http://localhost:8000/api/v1/custom-message?name=Byongho&language=Korean&key=YOUR_NFC_KEY" \
  -H "Content-Type: application/json" \
  -d '{"situation":"I am anxious about my future"}'
```

## Notes

- `.env` is ignored by Git and should not be committed.
- In production, pass environment variables via your platform secret manager or runtime environment.
