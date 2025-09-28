$ErrorActionPreference = 'Stop'
pip install -U pip ; pip install ruff black mypy
ruff check . ; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
black --check . ; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
mypy libs services ; if ($LASTEXITCODE -ne 0) { Write-Host "mypy had issues (non-blocking for now)" }
