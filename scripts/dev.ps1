# Dev server for llm-eval-playground
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
