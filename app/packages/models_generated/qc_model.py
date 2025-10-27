"""QC report model generated from schemas/qc_report.schema.json."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class QCMetric(BaseModel):
    """Aggregated QC metrics captured during evaluation."""

    groundedness: float = Field(..., ge=0, le=1)
    context_precision: float = Field(..., ge=0, le=1)
    wer: float = Field(..., ge=0)
    lufs: float
    true_peak_db: Optional[float] = Field(None, description="True peak in dB")
    duration_seconds: Optional[float] = Field(None, ge=0)

    @field_validator("lufs")
    @classmethod
    def validate_lufs(cls, v: float) -> float:
        """Ensure LUFS is a realistic value."""

        if not -60 <= v <= 0:
            raise ValueError("LUFS must be between -60 and 0 for podcast audio")
        return v


class QCIssue(BaseModel):
    """Individual QC issue item."""

    severity: str = Field(..., pattern=r"^(blocker|warning|info)$")
    message: str
    location: Optional[str] = None


class QCReport(BaseModel):
    """Top-level QC report object."""

    job_id: str
    timestamp: datetime
    passed: bool
    metrics: QCMetric
    issues: List[QCIssue] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    class Config:
        frozen = True
        json_schema_extra = {
            "example": {
                "job_id": "job_20251016_001",
                "timestamp": "2025-10-16T09:30:00Z",
                "passed": True,
                "metrics": {
                    "groundedness": 0.82,
                    "context_precision": 0.74,
                    "wer": 6.5,
                    "lufs": -16.2,
                    "true_peak_db": -1.3,
                    "duration_seconds": 3600,
                },
                "issues": [],
                "recommendations": [
                    "Spot-check Chapter 2 citations",
                    "Verify LUFS normalization on promo clips",
                ],
            }
        }