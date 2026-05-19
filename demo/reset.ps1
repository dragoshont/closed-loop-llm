# Reset demo memory to baseline. Use between rehearsals.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item -Path (Join-Path $here "memory.baseline.json") -Destination (Join-Path $here "memory.json") -Force
Write-Host "memory.json reset to baseline." -ForegroundColor Green
