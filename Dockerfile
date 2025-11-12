FROM python:3.10-slim

WORKDIR /app

# Install only essential packages
RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn==0.27.0 \
    pydantic==2.5.3 \
    pyyaml==6.0.1

# Copy only what we need
COPY src/api/main_minimal.py ./main.py

# Expose port
EXPOSE 8000

# Start - use shell form to allow env var substitution
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
