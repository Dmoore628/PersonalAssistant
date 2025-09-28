param(
    [switch]$Build
)

$ErrorActionPreference = 'Stop'

$envFile = Join-Path $PSScriptRoot '..' '.env'
if (!(Test-Path $envFile)) {
    Copy-Item (Join-Path $PSScriptRoot '..' '.env.example') $envFile
}

Push-Location (Join-Path $PSScriptRoot '..' 'infra')
try {
    if ($Build) {
        docker compose --env-file ../.env up --build -d
    } else {
        docker compose --env-file ../.env up -d
    }
}
finally {
    Pop-Location
}
