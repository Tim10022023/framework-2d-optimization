from fastapi import FastAPI

app = FastAPI(title="2D Optimization Framework")

@app.get("/")
def read_root():
    return {"message": "Backend läuft 🚀"}
