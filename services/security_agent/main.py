from fastapi import FastAPI
from archi_core import Settings, Health

settings = Settings()
app = FastAPI(title="Security Agent")

@app.get("/health", response_model=Health)
def health():
    return Health(service=settings.service_name or "security-agent", status="ok")
