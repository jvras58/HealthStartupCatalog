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
    startup: dict[str, any]  # Campos da startup
    traces: dict[str, dict[str, any]]  # Traces por campo
