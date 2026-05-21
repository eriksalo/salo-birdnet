import pytest
from app.db import queries


@pytest.mark.asyncio
async def test_get_dashboard_stats(db):
    stats = await queries.get_dashboard_stats(db)
    assert stats.total_detections == 7
    assert stats.total_species == 4


@pytest.mark.asyncio
async def test_get_recent_detections(db):
    detections = await queries.get_recent_detections(db, limit=5)
    assert len(detections) == 5
    assert detections[0].com_name in ("Eurasian Blackbird", "Great Tit", "European Robin")


@pytest.mark.asyncio
async def test_get_species_list(db):
    species = await queries.get_species_list(db)
    assert len(species) == 4
    names = {s.com_name for s in species}
    assert "Eurasian Blackbird" in names
    assert "Great Tit" in names


@pytest.mark.asyncio
async def test_get_detections_filtered_by_species(db):
    detections = await queries.get_detections_filtered(db, species="Eurasian Blackbird")
    assert all(d.com_name == "Eurasian Blackbird" for d in detections)
    assert len(detections) == 3


@pytest.mark.asyncio
async def test_get_detections_filtered_by_confidence(db):
    detections = await queries.get_detections_filtered(db, min_confidence=0.9)
    assert all(d.confidence >= 0.9 for d in detections)


@pytest.mark.asyncio
async def test_get_species_detail(db):
    detail = await queries.get_species_detail(db, "Great Tit")
    assert detail is not None
    assert detail.sci_name == "Parus major"
    assert detail.detection_count == 2


@pytest.mark.asyncio
async def test_get_daily_counts(db):
    counts = await queries.get_daily_counts(db, days=30)
    assert len(counts) > 0


@pytest.mark.asyncio
async def test_search_species(db):
    results = await queries.search_species(db, "black")
    assert len(results) == 1
    assert results[0].com_name == "Eurasian Blackbird"


@pytest.mark.asyncio
async def test_get_all_species_names(db):
    names = await queries.get_all_species_names(db)
    assert len(names) == 4
    assert names == sorted(names)


@pytest.mark.asyncio
async def test_keyset_pagination(db):
    page1 = await queries.get_detections_filtered(db, limit=3)
    assert len(page1) == 3
    last_id = page1[-1].id
    page2 = await queries.get_detections_filtered(db, last_id=last_id, limit=3)
    assert len(page2) == 3
    # No overlap
    page1_ids = {d.id for d in page1}
    page2_ids = {d.id for d in page2}
    assert page1_ids.isdisjoint(page2_ids)
