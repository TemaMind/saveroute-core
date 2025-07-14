import pytest, asyncio, uvicorn, multiprocessing, time, httpx, os

@pytest.fixture(scope="session", autouse=True)
def api_server():
    proc = multiprocessing.Process(
        target=uvicorn.run,
        args=("src.saveroute.api:app",),
        kwargs={"host": "127.0.0.1", "port": 8000, "log_level": "error"},
        daemon=True,
    )
    proc.start()
    time.sleep(1)  # give server time
    yield
    proc.terminate()

@pytest.mark.asyncio
async def test_check_endpoint():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "http://127.0.0.1:8000/v1/check",
            json={"description": "dual-use drone guidance unit"},
        )
        data = r.json()
        assert "risk_score" in data and "risk_label" in data
        assert 0 <= data["risk_score"] <= 1
