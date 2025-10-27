"""Auto-generated property-based tests verifying key data models."""

from __future__ import annotations

from datetime import datetime, timezone

from hypothesis import given, strategies as st
from hypothesis.strategies import SearchStrategy

from app.packages.models_generated import Chapter, Segment
from app.packages.models_generated.qc_model import QCReport, QCIssue, QCMetric


_lang_strategy = st.sampled_from(["en", "es", "fr", "de", "zh", "ja"])
_ascii_text = st.text(
	min_size=1,
	max_size=120,
	alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters=["\n", "\r"]),
)


class TestSegmentProperties:
	"""Property-based checks for the Segment model."""

	@given(
		start_ms=st.integers(min_value=0, max_value=100_000),
		duration_ms=st.integers(min_value=15_000, max_value=65_000),
		lang=_lang_strategy,
	)
	def test_duration_within_expected_window(self, start_ms: int, duration_ms: int, lang: str) -> None:
		segment = Segment(
			id="seg_prop",
			start_ms=float(start_ms),
			end_ms=float(start_ms + duration_ms),
			text="generated",
			lang=lang,
		)
		assert 15 <= segment.duration_seconds() <= 65

	@given(
		text=_ascii_text,
		lang=_lang_strategy,
	)
	def test_text_round_trip(self, text: str, lang: str) -> None:
		segment = Segment(
			id="seg_text",
			start_ms=0,
			end_ms=20_000,
			text=text,
			lang=lang,
		)
		assert segment.text == text
		assert segment.lang == lang


class TestChapterProperties:
	"""Property-based checks for the Chapter model."""

	@given(
		start_ms=st.integers(min_value=0, max_value=3_600_000),
		duration_ms=st.integers(min_value=1, max_value=3_600_000),
	)
	def test_chapter_duration_positive(self, start_ms: int, duration_ms: int) -> None:
		chapter = Chapter(
			id="chap_prop",
			title="Property Chapter",
			start_ms=start_ms,
			end_ms=start_ms + duration_ms,
		)
		assert chapter.duration_ms == duration_ms
		assert chapter.end_ms > chapter.start_ms


def _qc_metric_strategy() -> SearchStrategy[dict[str, object]]:
	return st.fixed_dictionaries(
		{
			"groundedness": st.floats(min_value=0, max_value=1),
			"context_precision": st.floats(min_value=0, max_value=1),
			"wer": st.floats(min_value=0, max_value=100),
			"lufs": st.floats(min_value=-60, max_value=0),
			"true_peak_db": st.one_of(st.none(), st.floats(min_value=-20, max_value=3)),
			"duration_seconds": st.one_of(st.none(), st.floats(min_value=0, max_value=14_400)),
		}
	)


def _qc_issue_strategy() -> SearchStrategy[dict[str, object]]:
	return st.fixed_dictionaries(
		{
			"severity": st.sampled_from(["blocker", "warning", "info"]),
			"message": _ascii_text,
			"location": st.one_of(st.none(), _ascii_text),
		}
	)


class TestQcReportProperties:
	"""Property-based checks for the QC report model."""

	@given(
		passed=st.booleans(),
		metrics=_qc_metric_strategy(),
		issues=st.lists(_qc_issue_strategy(), max_size=5),
		recommendations=st.lists(_ascii_text, max_size=5),
	)
	def test_qc_report_shapes(self, passed: bool, metrics: dict[str, object], issues: list[dict[str, object]], recommendations: list[str]) -> None:
		report = QCReport(
			job_id="job_prop",
			timestamp=datetime.now(tz=timezone.utc),
			passed=passed,
			metrics=QCMetric(**metrics),
			issues=[QCIssue(**issue) for issue in issues],
			recommendations=recommendations,
		)

		assert report.metrics.groundedness == metrics["groundedness"]
		if report.issues:
			severities = {issue.severity for issue in report.issues}
			assert severities <= {"blocker", "warning", "info"}
		for rec in report.recommendations:
			assert rec
