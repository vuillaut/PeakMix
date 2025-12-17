# Minimal production image for c2ccombos Flask webapp
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Copy metadata first for better layer caching
COPY pyproject.toml README.md /app/
COPY src /app/src

# Install runtime
RUN pip install --upgrade pip setuptools wheel \
    && pip install 'gunicorn>=21.2.0' \
    && pip install .

EXPOSE 8000

# Run the Flask app via gunicorn in production mode
# Use shell-form CMD so $PORT expands correctly at runtime
CMD gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT "c2ccombos.webapp:create_app()"
