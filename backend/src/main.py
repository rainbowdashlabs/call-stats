import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from web.app import router

app = FastAPI()

# Configure CORS
# You can set CORS_ORIGINS (comma-separated) env var, e.g.:
# CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your.site
# If not provided, sensible localhost defaults are used.

def _parse_origins(value):
    if not value:
        return None
    parts = [v.strip() for v in str(value).split(',')]
    origins = [v for v in parts if v]
    return origins or None


env_origins = _parse_origins(os.getenv('CORS_ORIGINS') or os.getenv('ALLOWED_ORIGINS'))
default_dev_origins = [
    '*',
]
origins = env_origins if env_origins is not None else default_dev_origins

# Allow credentials only when not using wildcard origins
allow_credentials = bool(origins and '*' not in origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ['*'],
    allow_credentials=allow_credentials,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router)
