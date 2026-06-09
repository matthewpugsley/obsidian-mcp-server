# deploy.ps1
$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) { throw ".env file not found. Copy .env.example to .env and fill in your values." }
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+?)\s*=\s*(.+?)\s*$') {
        [System.Environment]::SetEnvironmentVariable($Matches[1], $Matches[2])
    }
}

$source = $env:MCP_SOURCE
$dest   = $env:MCP_DEST
if (-not $source -or -not $dest) { throw "MCP_SOURCE and MCP_DEST must be set in .env" }

Write-Host "Deploying obsidian-mcp-server to $dest..." -ForegroundColor Cyan

robocopy $source $dest /E /XD .venv __pycache__ .git /XF "*.pyc"

Write-Host "Running uv sync..." -ForegroundColor Cyan
Push-Location $dest
$savedVirtualEnv = $env:VIRTUAL_ENV
$env:VIRTUAL_ENV = $null
uv sync
$env:VIRTUAL_ENV = $savedVirtualEnv
Pop-Location

Write-Host "Done. Restart Claude Desktop to pick up changes." -ForegroundColor Green
