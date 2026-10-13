from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import eval_runner as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, dataset_id: str | None = None, db: AsyncSession = Depends(get_db)):
    datasets = await svc.list_datasets(db)
    cases = await svc.list_cases(db, dataset_id) if dataset_id else []
    runs = await svc.list_runs(db, dataset_id)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "LLM Eval Playground", "datasets": datasets, "dataset_id": dataset_id, "cases": cases, "runs": runs},
    )

@router.post("/ui/datasets")
async def ui_ds(name: str = Form(...), db: AsyncSession = Depends(get_db)):
    row = await svc.create_dataset(db, name)
    return RedirectResponse(f"/?dataset_id={row.id}", status_code=303)

@router.post("/ui/cases")
async def ui_case(
    dataset_id: str = Form(...),
    prompt: str = Form(...),
    expected: str = Form(...),
    scorer: str = Form("contains"),
    db: AsyncSession = Depends(get_db),
):
    await svc.add_case(db, dataset_id, prompt, expected, scorer)
    return RedirectResponse(f"/?dataset_id={dataset_id}", status_code=303)

@router.post("/ui/run")
async def ui_run(dataset_id: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.run_dataset(db, dataset_id)
    return RedirectResponse(f"/?dataset_id={dataset_id}", status_code=303)
