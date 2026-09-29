$ErrorActionPreference = 'Stop'
$adminUrl = 'http://127.0.0.1:8091/admin.html'
function Test-AdminServer {
    try {
        $session = Invoke-RestMethod 'http://127.0.0.1:8091/api/admin/session' -TimeoutSec 2
        return $null -ne $session.authenticated
    } catch { return $false }
}
try {
    if (-not (Test-AdminServer)) {
        $pythonPath = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        if (-not (Test-Path -LiteralPath $pythonPath)) {
            $pythonPath = (Get-Command python -ErrorAction Stop).Source
        }
        Start-Process -FilePath $pythonPath -ArgumentList ('"' + (Join-Path $PSScriptRoot 'serve.py') + '"') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
        for ($attempt = 0; $attempt -lt 20; $attempt++) {
            if (Test-AdminServer) { break }
            Start-Sleep -Milliseconds 500
        }
        if (-not (Test-AdminServer)) { throw 'The admin server could not start on port 8091.' }
    }
    Start-Process $adminUrl
} catch {
    Write-Host $_.Exception.Message
    Read-Host 'Press Enter to close'
    exit 1
}
