import pytest

@pytest.mark.asyncio
async def test_eval_run(client):
    ds = await client.post("/api/datasets", json={"name": "smoke"})
    did = ds.json()["id"]
    await client.post(
        f"/api/datasets/{did}/cases",
        json={"prompt": "Say hello", "expected": "mock", "scorer": "contains"},
    )
    run = await client.post(f"/api/datasets/{did}/run")
    assert run.status_code == 200
    assert run.json()["total"] == 1
