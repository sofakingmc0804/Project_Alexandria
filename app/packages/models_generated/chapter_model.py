"""Chapter model derived from SPEC §6 data schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    """Episode chapter metadata."""

    id: str = Field(..., description="Chapter identifier")
    title: str = Field(..., min_length=1, description="Chapter title")
    start_ms: int = Field(..., ge=0, description="Start timestamp in ms")
    end_ms: int = Field(..., ge=0, description="End timestamp in ms")

    @property
    def duration_ms(self) -> int:
        """Duration of the chapter in milliseconds."""

        return self.end_ms - self.start_ms

    class Config:
        frozen = True
        json_schema_extra = {
            "example": {
                "id": "chapter_01",
                "title": "Introduction",
                "start_ms": 0,
                "end_ms": 300000,
            }
        }