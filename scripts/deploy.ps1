# Deploy Barbearia: Render (API) + Vercel (frontend)
# Required env vars:
#   DATABASE_URL  - Neon PostgreSQL connection string
#   RENDER_API_KEY - https://dashboard.render.com/u/settings#api-keys
#   VERCEL_TOKEN   - https://vercel.com/account/tokens (or run `npx vercel login` first)

$ErrorActionPreference = "Stop"

$Repo = "https://github.com/TyagoDy/Barbearia_Project"
$Branch = "develop"
$RenderServiceName = "barbearia-api"

function Require-Env($name) {
    if (-not (Get-Item "Env:$name" -ErrorAction SilentlyContinue)) {
        throw "Missing environment variable: $name"
    }
}

Require-Env "DATABASE_URL"
Require-Env "RENDER_API_KEY"

$renderHeaders = @{
    Authorization = "Bearer $env:RENDER_API_KEY"
    "Content-Type"  = "application/json"
}

Write-Host "==> Fetching Render owner..."
$owners = Invoke-RestMethod -Uri "https://api.render.com/v1/owners" -Headers $renderHeaders
if (-not $owners -or $owners.Count -eq 0) {
    throw "No Render owner found for this API key."
}
$ownerId = $owners[0].owner.id
Write-Host "    Owner: $($owners[0].owner.name) ($ownerId)"

Write-Host "==> Looking for existing Render service '$RenderServiceName'..."
$services = Invoke-RestMethod -Uri "https://api.render.com/v1/services?limit=100" -Headers $renderHeaders
$service = $services | ForEach-Object { $_.service } | Where-Object { $_.name -eq $RenderServiceName } | Select-Object -First 1

if (-not $service) {
    Write-Host "==> Creating Render Blueprint from $Repo ($Branch)..."
    $blueprintBody = @{
        ownerId    = $ownerId
        repo       = $Repo
        branch     = $Branch
        name       = "barbearia"
        autoDeploy = "yes"
    } | ConvertTo-Json
    $blueprint = Invoke-RestMethod -Method Post -Uri "https://api.render.com/v1/blueprints" -Headers $renderHeaders -Body $blueprintBody
    Write-Host "    Blueprint created. Sync in dashboard: https://dashboard.render.com/"
    Write-Host "    Waiting 90s for service provisioning..."
    Start-Sleep -Seconds 90
    $services = Invoke-RestMethod -Uri "https://api.render.com/v1/services?limit=100" -Headers $renderHeaders
    $service = $services | ForEach-Object { $_.service } | Where-Object { $_.name -eq $RenderServiceName } | Select-Object -First 1
    if (-not $service) {
        throw "Service '$RenderServiceName' not found after blueprint. Create it manually from render.yaml in the Render dashboard."
    }
}

$serviceId = $service.id
$backendUrl = "https://$($service.serviceDetails.url)"
Write-Host "    Backend URL: $backendUrl"

Write-Host "==> Setting Render env vars..."
function Set-RenderEnv($key, $value) {
    $body = @{ envVar = @{ key = $key; value = $value } } | ConvertTo-Json
    try {
        Invoke-RestMethod -Method Post -Uri "https://api.render.com/v1/services/$serviceId/env-vars" -Headers $renderHeaders -Body $body | Out-Null
    } catch {
        $list = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$serviceId/env-vars" -Headers $renderHeaders
        $existing = $list | ForEach-Object { $_.envVar } | Where-Object { $_.key -eq $key } | Select-Object -First 1
        if ($existing) {
            Invoke-RestMethod -Method Put -Uri "https://api.render.com/v1/services/$serviceId/env-vars/$($existing.id)" -Headers $renderHeaders -Body $body | Out-Null
        } else { throw }
    }
}

# CORS updated after Vercel deploy if FRONTEND_URL not set
$corsOrigins = "http://localhost:5173,http://127.0.0.1:5173"
if ($env:FRONTEND_URL) {
    $corsOrigins = "$env:FRONTEND_URL,$corsOrigins"
}
Set-RenderEnv "DATABASE_URL" $env:DATABASE_URL
Set-RenderEnv "CORS_ORIGINS" $corsOrigins

Write-Host "==> Triggering Render deploy..."
Invoke-RestMethod -Method Post -Uri "https://api.render.com/v1/services/$serviceId/deploys" -Headers $renderHeaders -Body "{}" | Out-Null

Write-Host "==> Deploying frontend to Vercel..."
$frontendDir = Join-Path $PSScriptRoot "..\frontend"
Push-Location $frontendDir
try {
    $vercelArgs = @("vercel", "deploy", "--prod", "--yes", "--build-env", "VITE_API_URL=$backendUrl")
    if ($env:VERCEL_TOKEN) {
        $vercelArgs += @("--token", $env:VERCEL_TOKEN)
    }
    & npx @vercelArgs
    if ($LASTEXITCODE -ne 0) { throw "Vercel deploy failed (exit $LASTEXITCODE)" }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Deploy started."
Write-Host "  Backend:  $backendUrl/health"
Write-Host "  Frontend: check Vercel output above for production URL"
Write-Host ""
Write-Host "After Vercel finishes, set CORS on Render:"
Write-Host "  CORS_ORIGINS=https://YOUR-APP.vercel.app,http://localhost:5173"
