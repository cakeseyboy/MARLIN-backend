import pytest
import asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db
from app.models import Base


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_client():
    # spin up a temp DB (sqlite memory) for speed
    url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(url, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _get_db():
        async with Session() as s:
            yield s

    app.dependency_overrides[get_db] = _get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_health_endpoint(test_client):
    """Test the health endpoint."""
    r = await test_client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_station_crud(test_client):
    """Test complete CRUD operations for weather stations."""
    # Create a station
    payload = {
        "code": "KLAX",
        "name": "Los Angeles Intl",
        "lat": 33.94,
        "lon": -118.40,
        "timezone": "America/Los_Angeles",
        "coastal_distance_km": 3.4,
    }
    r = await test_client.post("/stations/", json=payload)
    assert r.status_code == 201
    station_data = r.json()
    station_id = station_data["id"]
    assert station_data["code"] == "KLAX"
    assert station_data["name"] == "Los Angeles Intl"

    # Get the station by id
    r = await test_client.get(f"/stations/{station_id}")
    assert r.status_code == 200
    assert r.json()["code"] == "KLAX"

    # List all stations
    r = await test_client.get("/stations/")
    assert r.status_code == 200
    stations = r.json()
    assert len(stations) == 1
    assert stations[0]["code"] == "KLAX"

    # Test 404 for non-existent station
    r = await test_client.get("/stations/999")
    assert r.status_code == 404


@pytest.mark.anyio
async def test_tmax_crud(test_client):
    """Test CRUD operations for temperature calculations."""
    # First create a station
    station_payload = {
        "code": "KNYC",
        "name": "New York Central Park",
        "lat": 40.78,
        "lon": -73.97,
        "timezone": "America/New_York",
        "coastal_distance_km": 15.2,
    }
    r = await test_client.post("/stations/", json=station_payload)
    assert r.status_code == 201
    station_id = r.json()["id"]

    # Create a tmax calculation
    tmax_payload = {
        "station_id": station_id,
        "cli_forecast": 78.5,
        "method": "MARLIN_v1",
        "confidence": 0.85,
        "raw_payload": {"model": "GFS", "temp": 78.5, "humidity": 65},
    }
    r = await test_client.post("/tmax/", json=tmax_payload)
    assert r.status_code == 201
    tmax_data = r.json()
    assert tmax_data["station_id"] == station_id
    assert tmax_data["cli_forecast"] == 78.5
    assert tmax_data["method"] == "MARLIN_v1"
    assert tmax_data["confidence"] == 0.85
    assert "created_at" in tmax_data

    # List tmax calculations for the station
    r = await test_client.get(f"/tmax/station/{station_id}")
    assert r.status_code == 200
    calculations = r.json()
    assert len(calculations) == 1
    assert calculations[0]["cli_forecast"] == 78.5


@pytest.mark.anyio
async def test_station_validation(test_client):
    """Test input validation for weather stations."""
    # Test invalid station code (too short)
    invalid_payload = {
        "code": "KL",  # Too short
        "name": "Test Station",
        "lat": 33.94,
        "lon": -118.40,
        "timezone": "America/Los_Angeles",
        "coastal_distance_km": 3.4,
    }
    r = await test_client.post("/stations/", json=invalid_payload)
    assert r.status_code == 422

    # Test invalid station code (too long)
    invalid_payload["code"] = "TOOLONG"  # Too long
    r = await test_client.post("/stations/", json=invalid_payload)
    assert r.status_code == 422
