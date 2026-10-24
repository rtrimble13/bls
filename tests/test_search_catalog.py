from __future__ import annotations

from bls.catalog import CatalogEntry, bundled_surveys, series_catalog, survey_name
from bls.models import Survey
from bls.search import score_text, search_rows, search_series, search_surveys


def test_bundled_catalogs_are_well_formed() -> None:
    entries = series_catalog()
    assert len(entries) > 100
    ids = [e.series_id for e in entries]
    assert len(ids) == len(set(ids))
    assert all(e.survey == e.series_id[:2] for e in entries)
    surveys = bundled_surveys()
    assert Survey("CU", "Consumer Price Index - All Urban Consumers (CPI-U)") in surveys
    assert survey_name("ln") is not None and survey_name("ZZ") is None


def test_score_bands() -> None:
    assert score_text("core cpi", "anything", ["core cpi"]) == 100.0
    assert score_text("Unemployment Rate", "unemployment rate") == 100.0
    assert score_text("core cpi", "All items less food and energy (core CPI)") == 95.0
    assert score_text("employ", "Employment level") == 75.0
    typo = score_text("unemploymnt rate", "Unemployment rate, 16 years and over")
    assert 80 < typo < 90
    assert score_text("zzzz", "Unemployment rate") == 0.0
    assert score_text("", "x") == 0.0


def test_search_series_rankings() -> None:
    entries = series_catalog()
    top = search_series("core cpi", entries, limit=2)
    assert {h.id for h in top} == {"CUSR0000SA0L1E", "CUUR0000SA0L1E"}
    assert search_series("unemploymnt rate", entries, limit=1)[0].id == "LNS14000000"
    assert search_series("nonfarm payrolls", entries, limit=1)[0].id == "CES0000000001"
    assert search_series("gas price", entries, limit=1)[0].id == "APU000074714"
    assert search_series("LNS14000000", entries)[0].score == 100.0
    assert all(
        h.survey == "LA" for h in search_series("unemployment", entries, survey="la", limit=0)
    )
    assert search_series("zzzz qqqq", entries) == []
    rec = top[0].to_record()
    assert rec["kind"] == "series" and "frequency" in rec and "score" in rec


def test_search_surveys() -> None:
    surveys = bundled_surveys()
    assert search_surveys("cu", surveys)[0].id == "CU"
    hits = search_surveys("producer price", surveys, limit=0)
    assert {h.id for h in hits} >= {"WP", "PC"}
    assert all(h.kind == "survey" for h in hits)


def test_search_rows_generic() -> None:
    rows = [
        {"series_id": "A1", "series_title": "Gasoline all types"},
        {"series_id": "B2", "series_title": "Bread"},
    ]
    hits = search_rows(
        "gasoline", rows, text_of=lambda r: r["series_title"], id_of=lambda r: r["series_id"]
    )
    assert [r["series_id"] for _, r in hits] == ["A1"]
    assert (
        search_rows(
            "b2", rows, text_of=lambda r: r["series_title"], id_of=lambda r: r["series_id"]
        )[0][0]
        == 100.0
    )


def test_catalog_entry_record() -> None:
    e = CatalogEntry("X", "t", "XX", "monthly", "SA", "u", ("a",))
    assert e.to_record()["tags"] == ["a"]
    assert "XX" in e.search_text
