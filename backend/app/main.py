from fastapi import FastAPI

from app.api.functions import router as functions_router
from app.api.sessions import router as sessions_router

app = FastAPI(title="2D Optimization Framework")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(functions_router)
app.include_router(sessions_router)
