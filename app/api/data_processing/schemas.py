from typing import Any

from pydantic import BaseModel


class DataProcessRequest(BaseModel):
    input_text: str


class DataProcessResponse(BaseModel):
    processed_result: str


class CatalogRequest(BaseModel):
    url: str | None
    clues: str | None
    # PDF via UploadFile no endpoint


class CatalogResponse(BaseModel):
    startup: dict[str, Any]  # Campos da startup
    traces: dict[str, dict[str, Any]]  # Traces por campo
