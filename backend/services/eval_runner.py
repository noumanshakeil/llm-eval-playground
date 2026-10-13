from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import EvalCase, EvalDataset, EvalResult, EvalRun
from backend.services.scorers import run_scorer
from backend.utils.ids import short_id

async def create_dataset(session: AsyncSession, name: str, description: str = "") -> EvalDataset:
    ds = EvalDataset(id=short_id(), name=name.strip()[:160], description=description.strip())
    session.add(ds)
    await session.commit()
    await session.refresh(ds)
    return ds

async def list_datasets(session: AsyncSession) -> list[EvalDataset]:
    return list((await session.execute(select(EvalDataset).order_by(EvalDataset.name))).scalars())

async def add_case(
    session: AsyncSession, dataset_id: str, prompt: str, expected: str, scorer: str = "contains"
) -> EvalCase:
    case = EvalCase(
        id=short_id(),
        dataset_id=dataset_id,
        prompt=prompt.strip(),
        expected=expected.strip(),
        scorer=scorer if scorer in {"exact", "contains", "length"} else "contains",
    )
    session.add(case)
    await session.commit()
    await session.refresh(case)
    return case

async def list_cases(session: AsyncSession, dataset_id: str) -> list[EvalCase]:
    stmt = select(EvalCase).where(EvalCase.dataset_id == dataset_id).order_by(EvalCase.created_at)
    return list((await session.execute(stmt)).scalars())

async def list_runs(session: AsyncSession, dataset_id: str | None = None) -> list[EvalRun]:
    stmt = select(EvalRun)
    if dataset_id:
        stmt = stmt.where(EvalRun.dataset_id == dataset_id)
    return list((await session.execute(stmt.order_by(EvalRun.created_at.desc()))).scalars())

async def run_dataset(session: AsyncSession, dataset_id: str) -> dict:
    ds = await session.get(EvalDataset, dataset_id)
    if not ds:
        raise ValueError("dataset not found")
    cases = await list_cases(session, dataset_id)
    llm = get_llm()
    run = EvalRun(id=short_id(), dataset_id=dataset_id, total=len(cases))
    session.add(run)
    await session.flush()
    passed = 0
    for case in cases:
        actual = await llm.complete(case.prompt, system="Answer briefly for evaluation.")
        sc = run_scorer(case.scorer, case.expected, actual)
        ok = sc >= 0.999
        if ok:
            passed += 1
        session.add(
            EvalResult(
                run_id=run.id,
                case_id=case.id,
                score=sc,
                actual=actual[:4000],
                passed=1 if ok else 0,
            )
        )
    run.passed = passed
    run.pass_rate = (passed / len(cases)) if cases else 0.0
    await session.commit()
    return {"run_id": run.id, "total": run.total, "passed": passed, "pass_rate": run.pass_rate}
