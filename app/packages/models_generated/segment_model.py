"""Segment model generated from schemas/segment.schema.json."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Segment(BaseModel):
    """Audio segment metadata used throughout the pipeline."""

    id: str = Field(..., description="Unique segment identifier")
    start_ms: float = Field(..., ge=0, description="Start time in milliseconds")
    end_ms: float = Field(..., ge=0, description="End time in milliseconds")
    text: str = Field(..., min_length=1, description="Segment transcript text")
    lang: str = Field(
        ...,
        pattern=r"^[a-z]{2}(-[A-Z]{2})?$",
        description="Language code (ISO 639-1 with optional region)",
    )
    source_file: Optional[str] = Field(None, description="Origin audio file")
    speaker_id: Optional[str] = Field(None, description="Speaker/host identifier")
    embedding_vector_ref: Optional[str] = Field(
        None, description="Reference to stored embedding vector"
    )
    confidence: Optional[float] = Field(
        None, ge=0, le=1, description="ASR confidence score between 0 and 1"
    )

    @field_validator("end_ms")
    @classmethod
    def validate_duration(cls, v: float, info: ValidationInfo) -> float:
        """Ensure each segment duration falls within the 15-65s window."""

        start = (info.data or {}).get("start_ms")
        if start is None:
            return v
        duration = v - start
        if not 15_000 <= duration <= 65_000:
            raise ValueError(
                f"Segment duration must be between 15000 and 65000 ms, got {duration}."
            )
        return v

    def duration_ms(self) -> float:
        """Return duration in milliseconds."""

        return self.end_ms - self.start_ms

    def duration_seconds(self) -> float:
        """Return duration in seconds."""

        return self.duration_ms() / 1000

    class Config:
        frozen = True
        json_schema_extra = {
            "example": {
                "id": "seg_001",
                "start_ms": 0,
                "end_ms": 32000,
                "text": "Welcome to Project Alexandria",
                "lang": "en",
                "source_file": "episode_001.wav",
                "speaker_id": "host_a",
                "confidence": 0.97,
            }
        }