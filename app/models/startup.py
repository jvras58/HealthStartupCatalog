from typing import TYPE_CHECKING

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.utils.base_model import AbstractBaseModel

if TYPE_CHECKING:
    pass


class Startup(AbstractBaseModel):
    __tablename__ = 'startups'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, name='id'
    )
    name: Mapped[str] = mapped_column(String, index=True, name='name')
    description: Mapped[str] = mapped_column(Text, name='description')
    website: Mapped[str] = mapped_column(String, name='website')
    founders: Mapped[dict] = mapped_column(
        JSON, name='founders'
    )  # Lista de dicts: [{"name": str, "role": str}]
    stage: Mapped[str] = mapped_column(
        String, name='stage'
    )  # ex.: "Seed", "Series A"
    health_focus: Mapped[str] = mapped_column(
        String, name='health_focus'
    )  # ex.: "Telecardiologia"
    confidence_traces: Mapped[dict] = mapped_column(
        JSON, name='confidence_traces'
    )  # Dict de traces por campo


class InferenceHistory(AbstractBaseModel):
    __tablename__ = 'inference_history'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, name='id'
    )
    startup_id: Mapped[int] = mapped_column(
        Integer, index=True, name='startup_id'
    )
    inference_json: Mapped[dict] = mapped_column(
        JSON, name='inference_json'
    )  # Full trace da execução
    processed_at: Mapped[str] = mapped_column(
        server_default=func.now(), name='processed_at'
    )
