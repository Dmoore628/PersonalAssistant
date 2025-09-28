$ErrorActionPreference = 'Stop'

Push-Location (Join-Path $PSScriptRoot '..' 'infra')
try {
    docker compose --env-file ../.env down -v
}
finally {
    Pop-Location
}
