# CodeHouses - One-Click Launcher
# Right-click -> "Run with PowerShell" to start everything

$Root     = $PSScriptRoot
$Backend  = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Chatbot  = Join-Path $Root "chatbot"

function Log($msg, $color = "Cyan") { Write-Host "  $msg" -ForegroundColor $color }
function Header($msg) {
    Write-Host ""
    Write-Host "  ======================================" -ForegroundColor DarkGray
    Write-Host "  $msg" -ForegroundColor Yellow
    Write-Host "  ======================================" -ForegroundColor DarkGray
}

Clear-Host
Write-Host ""
Write-Host "  CodeHouses Platform Launcher" -ForegroundColor Magenta
Write-Host "  --------------------------------------" -ForegroundColor DarkGray

# 1. Execution policy
Header "Checking PowerShell execution policy..."
$effectivePolicy = Get-ExecutionPolicy
$allowedPolicies = @("Bypass", "Unrestricted", "RemoteSigned")
if ($allowedPolicies -contains $effectivePolicy) {
    Log "Execution policy OK ($effectivePolicy)" Green
} else {
    try {
        Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force -ErrorAction Stop
        Log "Execution policy set to RemoteSigned OK" Green
    } catch {
        Log "Execution policy override detected ($effectivePolicy) - continuing..." Yellow
    }
}

# 2. MongoDB (for Flask backend)
Header "Starting MongoDB..."
$mongoService = Get-Service -Name "MongoDB" -ErrorAction SilentlyContinue
if ($mongoService) {
    if ($mongoService.Status -ne "Running") {
        try {
            Start-Service MongoDB -ErrorAction Stop
            Log "MongoDB service started OK" Green
        } catch {
            Log "Needs Administrator to start MongoDB. Prompting for elevation..." Yellow
            try {
                Start-Process powershell -Verb RunAs -ArgumentList "-WindowStyle Hidden -Command Start-Service MongoDB" -Wait
                $checkService = Get-Service -Name "MongoDB"
                if ($checkService.Status -eq "Running") {
                    Log "MongoDB service started OK" Green
                } else {
                    Log "Failed to start MongoDB. You may need to run this script as Administrator." Red
                }
            } catch {
                Log "Elevation cancelled or failed. Backend might not work." Red
            }
        }
    } else {
        Log "MongoDB service already running OK" Green
    }
} else {
    $mongodExe = Get-Command mongod -ErrorAction SilentlyContinue
    if ($mongodExe) {
        $dataPath = "C:\data\db"
        if (-not (Test-Path $dataPath)) { New-Item -ItemType Directory -Path $dataPath | Out-Null }
        Start-Process -FilePath "mongod" -ArgumentList "--dbpath `"$dataPath`"" -WindowStyle Minimized
        Log "mongod launched in background OK" Green
        Start-Sleep -Seconds 2
    } else {
        Log "WARNING: MongoDB not found! Please install MongoDB and add it to PATH." Red
        Log "   Download: https://www.mongodb.com/try/download/community" Red
        Read-Host "  Press Enter to continue anyway (backend may fail)..."
    }
}

# 3. Online Compiler (Docker Compose — Judge0 + Judge Service)
Header "Starting Online Compiler services (Docker + Judge0)..."
$dockerExe = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerExe) {
    $dockerRunning = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Log "Docker is running. Starting Judge0 + compiler services..." Cyan
        Log "  This takes 2-3 minutes on first run (Judge0 image download)" Yellow
        Start-Process powershell -ArgumentList `
            "-NoExit", `
            "-Command", `
            "Write-Host '  Judge0 + Compiler Services' -ForegroundColor Blue; Set-Location '$Root'; docker compose up --build 2>&1" `
            -WindowStyle Normal
        Log "Docker Compose window opened." Green
        Log "  Wait for: 'judge0_server  | Listening on...' before submitting code" Yellow
        Log "  Judge0 API  -> http://localhost:2358" DarkGray
        Log "  Judge Svc   -> http://localhost:8002" DarkGray
        Log "  Leaderboard -> http://localhost:8003" DarkGray
        Start-Sleep -Seconds 3
    } else {
        Log "WARNING: Docker Desktop is not running." Yellow
        Log "  Start Docker Desktop, then re-run this script to enable Judge0." Yellow
        Log "  Without Docker: only Python, Java, JavaScript work (local fallback)." Yellow
    }
} else {
    Log "WARNING: Docker not installed." Yellow
    Log "  Install Docker Desktop: https://www.docker.com/products/docker-desktop/" Yellow
    Log "  Without Docker: only Python, Java, JavaScript work (local fallback)." Yellow
}

# 4. Flask backend - venv + deps
Header "Setting up Python backend..."
$venvPath = Join-Path $Backend "venv"
if (-not (Test-Path $venvPath)) {
    Log "Creating virtual environment..." Cyan
    & python -m venv $venvPath
    Log "Virtual environment created OK" Green
} else {
    Log "Virtual environment exists OK" Green
}

$pip = Join-Path $venvPath "Scripts\pip.exe"
Log "Installing Python dependencies..." Cyan
& $pip install -q -r (Join-Path $Backend "requirements.txt")
Log "Python dependencies ready OK" Green

# 5. Frontend - npm install
Header "Setting up Node.js frontend..."
$nodeModules = Join-Path $Frontend "node_modules"
if (-not (Test-Path $nodeModules)) {
    Log "Running npm install (first time - may take 1-2 minutes)..." Cyan
    Push-Location $Frontend
    & npm install --silent
    Pop-Location
    Log "npm packages installed OK" Green
} else {
    Log "node_modules exists OK" Green
}

# 6. Launch Flask backend
Header "Launching backend server (port 5000)..."
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$appPy     = Join-Path $Backend "app.py"
# Set MONGO_URI to localhost for local dev (not the Docker 'mongo' hostname)
$env:MONGO_URI = "mongodb://localhost:27017/coding_platform"
Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "`$env:MONGO_URI='mongodb://localhost:27017/coding_platform'; Write-Host '  Flask Backend' -ForegroundColor Cyan; & '$pythonExe' '$appPy'" `
    -WindowStyle Normal
Log "Backend window opened OK" Green
Start-Sleep -Seconds 3

# 7. Launch React frontend
Header "Launching React frontend (port 3000)..."
Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Write-Host '  React Frontend' -ForegroundColor Cyan; Set-Location '$Frontend'; npm start" `
    -WindowStyle Normal
Log "Frontend window opened OK" Green
Start-Sleep -Seconds 2

# 8. Chatbot - npm install if needed
Header "Setting up AI Mentor chatbot (Next.js)..."
$chatbotModules = Join-Path $Chatbot "node_modules"
if (-not (Test-Path $chatbotModules)) {
    Log "Running npm install for chatbot (first time)..." Cyan
    Push-Location $Chatbot
    & npm install --silent
    Pop-Location
    Log "Chatbot npm packages installed OK" Green
} else {
    Log "Chatbot node_modules exists OK" Green
}

# 9. Launch chatbot
Header "Launching AI Mentor chatbot (port 3001)..."
Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "Write-Host '  AI Mentor Chatbot' -ForegroundColor Magenta; Set-Location '$Chatbot'; npm run dev" `
    -WindowStyle Normal
Log "Chatbot window opened OK" Green
Start-Sleep -Seconds 4

# 10. Open browser
Header "Opening browser..."
Start-Process "http://localhost:3000"
Log "Browser launched -> http://localhost:3000 OK" Green

# Done
Write-Host ""
Write-Host "  CodeHouses is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend        -> http://localhost:5000" -ForegroundColor DarkGray
Write-Host "  Frontend       -> http://localhost:3000" -ForegroundColor DarkGray
Write-Host "  AI Mentor      -> http://localhost:3001" -ForegroundColor Magenta
Write-Host "  Compiler API   -> http://localhost:8002  (Docker)" -ForegroundColor Blue
Write-Host "  Gateway        -> http://localhost:80    (Docker)" -ForegroundColor Blue
Write-Host ""
Write-Host "  To stop: close the PowerShell windows that opened." -ForegroundColor DarkGray
Write-Host "  To stop Docker: run 'docker compose down' in this folder." -ForegroundColor DarkGray
Write-Host ""
Read-Host "  Press Enter to close this launcher"
