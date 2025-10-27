"""Hypothesis-based property tests for generated Pydantic models."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from hypothesis import given, settings, strategies as st
from pydantic import ValidationError

from app.packages.models_generated.chapter_model import Chapter
from app.packages.models_generated.qc_model import QCMetric, QCReport
from app.packages.models_generated.segment_model import Segment


valid_langs = st.sampled_from(["en", "es", "fr", "de", "pt", "en-US"])


@settings(deadline=None)
@given(
    start_ms=st.integers(min_value=0, max_value=1_000_000),
    duration_ms=st.integers(min_value=15_000, max_value=65_000),
    text=st.text(min_size=1, max_size=256),
    lang=valid_langs,
)
def test_segment_duration_within_bounds(start_ms: int, duration_ms: int, text: str, lang: str) -> None:
    segment = Segment(
        id="seg_property",
        start_ms=start_ms,
        end_ms=start_ms + duration_ms,
        text=text,
        lang=lang,
    )

    assert segment.duration_ms() == pytest.approx(duration_ms)
    assert round(segment.duration_seconds(), 3) == pytest.approx(duration_ms / 1000, rel=1e-3)


@settings(deadline=None)
@given(
    start_ms=st.floats(min_value=0, max_value=1_000_000, allow_nan=False, allow_infinity=False),
    duration_ms=st.floats(min_value=0, max_value=14_999, allow_nan=False, allow_infinity=False),
    text=st.text(min_size=1, max_size=64),
)
def test_segment_invalid_duration_rejected(start_ms: float, duration_ms: float, text: str) -> None:
    with pytest.raises(ValidationError):
        Segment(
            id="seg_invalid",
            start_ms=start_ms,
            end_ms=start_ms + duration_ms,
            text=text,
            lang="en",
        )


@settings(deadline=None)
@given(
    start_ms=st.integers(min_value=0, max_value=3_600_000),
    duration_ms=st.integers(min_value=1_000, max_value=900_000),
    title=st.text(min_size=1, max_size=80),
)
def test_chapter_duration_property(start_ms: int, duration_ms: int, title: str) -> None:
    chapter = Chapter(
        id="chapter_property",
        title=title,
        start_ms=start_ms,
        end_ms=start_ms + duration_ms,
    )

    assert chapter.duration_ms == duration_ms


@settings(deadline=None)
@given(
    groundedness=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    context_precision=st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    wer=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
    lufs=st.floats(min_value=-40, max_value=-10, allow_nan=False, allow_infinity=False),
    true_peak=st.floats(min_value=-6, max_value=0, allow_nan=False, allow_infinity=False),
    duration_seconds=st.floats(min_value=0, max_value=7_200, allow_nan=False, allow_infinity=False),
)
def test_qc_report_accepts_realistic_metrics(
    groundedness: float,
    context_precision: float,
    wer: float,
    lufs: float,
    true_peak: float,
    duration_seconds: float,
) -> None:
    metrics = QCMetric(
        groundedness=groundedness,
        context_precision=context_precision,
        wer=wer,
        lufs=lufs,
        true_peak_db=true_peak,
        duration_seconds=duration_seconds,
    )

    report = QCReport(
        job_id="job_property",
        timestamp=datetime.now(timezone.utc),
        passed=True,
        metrics=metrics,
        issues=[],
    )

    assert report.metrics.lufs == pytest.approx(lufs)
    assert report.metrics.duration_seconds == pytest.approx(duration_seconds)


@settings(deadline=None)
@given(lufs=st.one_of(st.floats(max_value=-100, allow_nan=False, allow_infinity=False), st.floats(min_value=5, allow_nan=False, allow_infinity=False)))
def test_qc_metric_rejects_unrealistic_lufs(lufs: float) -> None:
    with pytest.raises(ValidationError):
        QCMetric(
            groundedness=0.8,
            context_precision=0.8,
            wer=5.0,
            lufs=lufs,
        )
