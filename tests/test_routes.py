import pytest


@pytest.mark.asyncio
async def test_dashboard(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "BirdNET" in resp.text
    assert "Today" in resp.text


@pytest.mark.asyncio
async def test_detections_page(client):
    resp = await client.get("/detections/")
    assert resp.status_code == 200
    assert "Detection History" in resp.text


@pytest.mark.asyncio
async def test_species_page(client):
    resp = await client.get("/species/")
    assert resp.status_code == 200
    assert "Eurasian Blackbird" in resp.text


@pytest.mark.asyncio
async def test_species_detail(client):
    resp = await client.get("/species/Great Tit")
    assert resp.status_code == 200
    assert "Parus major" in resp.text


@pytest.mark.asyncio
async def test_species_not_found(client):
    resp = await client.get("/species/Nonexistent Bird")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_species_search(client):
    resp = await client.get("/species/search?q=robin")
    assert resp.status_code == 200
    assert "European Robin" in resp.text


@pytest.mark.asyncio
async def test_charts_page(client):
    resp = await client.get("/charts/")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_charts_daily_data(client):
    resp = await client.get("/charts/data/daily?days=30")
    assert resp.status_code == 200
    data = resp.json()
    assert "labels" in data
    assert "data" in data


@pytest.mark.asyncio
async def test_charts_hourly_data(client):
    resp = await client.get("/charts/data/hourly")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["labels"]) == 24


@pytest.mark.asyncio
async def test_api_stats(client):
    resp = await client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_detections"] == 7


@pytest.mark.asyncio
async def test_detection_rows_htmx(client):
    resp = await client.get("/detections/rows?species=Eurasian Blackbird")
    assert resp.status_code == 200
    assert "Eurasian Blackbird" in resp.text


@pytest.mark.asyncio
async def test_config_page(client):
    resp = await client.get("/config/")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_system_page(client):
    resp = await client.get("/system/")
    assert resp.status_code == 200
    assert "System Information" in resp.text
