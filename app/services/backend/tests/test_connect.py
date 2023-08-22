import json
import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_read_main():
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        assert response.json() == ['Connect']
