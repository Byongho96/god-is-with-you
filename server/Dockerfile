FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies for this FastAPI app.
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    google-generativeai \
    python-dotenv \
    pydantic

COPY main.py schemas.py /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
