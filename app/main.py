from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/healthz")
async def healthz():
    return {"status": "healthy"}