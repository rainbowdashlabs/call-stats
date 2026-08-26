import os

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/config", tags=["config"])


class AppConfig(BaseModel):
    """Display settings the frontend needs before anyone has logged in."""
    brigade_name: str


@router.get("")
def get_config() -> AppConfig:
    return AppConfig(brigade_name=os.getenv("BRIGADE_NAME", ""))
