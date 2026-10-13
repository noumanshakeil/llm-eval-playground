from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import eval_runner as svc

class DatasetIn(BaseModel):
    name: str = Field(min_length=2)
    description: str = ""

class CaseIn(BaseModel):
    prompt: str = Field(min_length=3)
    expected: str = Field(min_length=1)
    scorer: str = "contains"

router = APIRouter()

@router.get("/datasets")
async def datasets(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_datasets(db)
    return {"datasets": [{"id": d.id, "name": d.name, "description": d.description} for d in rows]}

@router.post("/datasets")
async def create_dataset(payload: DatasetIn, db: AsyncSession = Depends(get_db)):
    row = await svc.create_dataset(db, payload.name, payload.description)
    return {"id": row.id, "name": row.name}

@router.get("/datasets/{dataset_id}/cases")
async def cases(dataset_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_cases(db, dataset_id)
    return {
        "cases": [
            {"id": c.id, "prompt": c.prompt, "expected": c.expected, "scorer": c.scorer} for c in rows
        ]
    }

@router.post("/datasets/{dataset_id}/cases")
async def add_case(dataset_id: str, payload: CaseIn, db: AsyncSession = Depends(get_db)):
    row = await svc.add_case(db, dataset_id, payload.prompt, payload.expected, payload.scorer)
    return {"id": row.id}

@router.get("/runs")
async def runs(dataset_id: str | None = None, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_runs(db, dataset_id)
    return {
        "runs": [
            {
                "id": r.id,
                "dataset_id": r.dataset_id,
                "pass_rate": r.pass_rate,
                "passed": r.passed,
                "total": r.total,
            }
            for r in rows
        ]
    }

@router.post("/datasets/{dataset_id}/run")
async def run_eval(dataset_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await svc.run_dataset(db, dataset_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
