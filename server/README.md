# Bible Verse & Comfort API

A FastAPI service that generates Bible verses using Gemini, with optional personalization by `name` and output translation by `language`.

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

- `name` (optional)
- `language` (optional, default: `Korean`)

Example:

```bash
curl "http://localhost:8000/api/v1/daily-verse?name=Byongho&language=Korean"
```

### `POST /api/v1/custom-message`

Query parameters:

- `name` (optional)
- `language` (optional, default: `Korean`)

JSON body:

- `situation` (optional)

Example:

```bash
curl -X POST "http://localhost:8000/api/v1/custom-message?name=Byongho&language=Korean" \
  -H "Content-Type: application/json" \
  -d '{"situation":"I am anxious about my future"}'
```

## Notes

- `.env` is ignored by Git and should not be committed.
- In production, pass environment variables via your platform secret manager or runtime environment.
