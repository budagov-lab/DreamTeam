# DreamTeam — Autonomous Development Cruiser Setup
# Run this from the DreamTeam root folder: .\setup.ps1

$ErrorActionPreference = "Stop"
Clear-Host

Write-Host "=====================================================" -ForegroundColor Magenta
Write-Host "   DreamTeam Cruiser Engine Setup (Windows)" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Magenta

# Check Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Python not found. Please install Python 3.10+ and add to PATH." -ForegroundColor Red
    exit 1
}

# Check Git
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Git not found. Git-Ops agent requires git.exe in PATH." -ForegroundColor Yellow
}

Write-Host "`nInstalling engine with RAG and Multi-Agent support..." -ForegroundColor Gray
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[!] Installation failed. Check your pip/internet connection." -ForegroundColor Red
    exit 1
}

Write-Host "`nVerifying CLI commands..." -ForegroundColor Gray
python -m dreamteam --help | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] CLI verification failed." -ForegroundColor Red
    exit 1
}

# Try to add Python Scripts to current session Path
$scriptsPath = python -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null
if ($scriptsPath -and (Test-Path $scriptsPath)) {
    $env:Path = "$scriptsPath;$env:Path"
}

Write-Host "`nDONE! DreamTeam Cruiser is ready for take-off." -ForegroundColor Green
Write-Host "-----------------------------------------------------" -ForegroundColor Gray
Write-Host "Next steps to start a project:" -ForegroundColor White
Write-Host "  1. Create a NEW empty folder for your project." -ForegroundColor Gray
Write-Host "  2. Go there: " -NoNewline -ForegroundColor Gray; Write-Host "cd C:\Projects\MyNewApp" -ForegroundColor White
Write-Host "  3. Deploy:  " -NoNewline -ForegroundColor Gray; Write-Host "python -m dreamteam new-project ." -ForegroundColor White
Write-Host "  4. Dashboard: " -NoNewline -ForegroundColor Gray; Write-Host "python -m dreamteam dashboard" -ForegroundColor White
Write-Host "-----------------------------------------------------" -ForegroundColor Gray
Write-Host "Note: Do NOT run project commands inside the DreamTeam engine folder." -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Magenta
