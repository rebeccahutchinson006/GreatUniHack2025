# PowerShell script to run both frontend and backend servers

Write-Host "Starting Music Discovery App..." -ForegroundColor Green
Write-Host ""

# Check if backend .env file exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "WARNING: backend\.env file not found!" -ForegroundColor Yellow
    Write-Host "Please copy backend\.env.example to backend\.env and add your Spotify credentials" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Do you want to continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit
    }
}

# Start backend server in a new terminal
Write-Host "Starting Backend Server (http://localhost:8000)..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend; python server.py"

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start frontend server in a new terminal
Write-Host "Starting Frontend Server (http://localhost:5173)..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "npm run dev"

Write-Host ""
Write-Host "Both servers are starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Blue
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Blue
Write-Host ""
Write-Host "Press any key to exit this script (servers will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
