from fastapi import FastAPI

from app.api.functions import router as functions_router
from app.api.sessions import router as sessions_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="2D Optimization Framework")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite (Frontend)
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # falls du mal CRA nutzt
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(functions_router)
app.include_router(sessions_router)
