from archi_core import Health, Settings
from fastapi import FastAPI

settings = Settings()
app = FastAPI(title="Tool Creation Agent")


@app.get("/health", response_model=Health)
def health():
    return Health(service=settings.service_name or "tool-creation-agent", status="ok")
