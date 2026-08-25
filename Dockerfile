# Stage 1: Install frontend dependencies (cached unless package.json changes)
FROM node:24-alpine AS frontend-deps
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Stage 2: Build frontend (only reruns when src changes)
FROM frontend-deps AS frontend-build
COPY frontend/ ./
RUN npm run build

# Stage 3: Install Python dependencies (cached unless Pipfile changes)
FROM python:3.14-slim AS backend-deps
WORKDIR /app
RUN pip install --no-cache-dir pipenv
COPY backend/Pipfile backend/Pipfile.lock ./
RUN pipenv sync --system && pip uninstall -y pipenv

# Stage 4: Final image — backend + built frontend
FROM backend-deps AS production
WORKDIR /app

# Copy backend source (changes frequently, but layer is small)
COPY backend/src/ ./src/

# Copy built frontend from stage 2
COPY --from=frontend-build /app/dist ./static/

EXPOSE 8000

CMD ["uvicorn", "--app-dir", "src", "main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --start-period=10s --interval=30s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/auth/login')" || exit 1
