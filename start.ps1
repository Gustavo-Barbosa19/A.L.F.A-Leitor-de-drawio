param(
    [switch]$Docker,
    [switch]$Dev
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IA RAG - Leitor de Draw.io" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[!] Arquivo .env criado a partir de .env.example" -ForegroundColor Yellow
    Write-Host "    Edite .env com sua OPENAI_API_KEY se desejar usar LLM" -ForegroundColor Yellow
    Write-Host ""
}

if ($Docker) {
    Write-Host "[*] Iniciando com Docker..." -ForegroundColor Green
    docker-compose up -d --build
    Write-Host ""
    Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Green
    Write-Host "  API:      http://localhost:8000" -ForegroundColor Green
    Write-Host "  Docs:     http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "  Qdrant:   http://localhost:6333" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para parar: docker-compose down" -ForegroundColor Yellow
}
elseif ($Dev) {
    Write-Host "[*] Iniciando em modo desenvolvimento..." -ForegroundColor Green
    Write-Host ""

    Write-Host "[1/3] Verificando dependencias do backend..." -ForegroundColor Yellow
    if (-not (Test-Path "backend\venv")) {
        python -m venv backend\venv
        & .\backend\venv\Scripts\pip install -r backend\requirements.txt
    }

    Write-Host "[2/3] Verificando dependencias do frontend..." -ForegroundColor Yellow
    if (-not (Test-Path "frontend\node_modules")) {
        cd frontend
        npm install
        cd ..
    }

    Write-Host "[3/3] Iniciando servicos..." -ForegroundColor Yellow
    Write-Host ""

    $backendJob = Start-Job -ScriptBlock {
        cd $using:PWD\backend
        .\venv\Scripts\Activate.ps1
        python -m app.main
    }

    $frontendJob = Start-Job -ScriptBlock {
        cd $using:PWD\frontend
        npm run dev
    }

    Write-Host "  Backend iniciado como job: $($backendJob.Id)" -ForegroundColor Green
    Write-Host "  Frontend iniciado como job: $($frontendJob.Id)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Green
    Write-Host "  API:      http://localhost:8000" -ForegroundColor Green
    Write-Host "  Docs:     http://localhost:8000/docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para parar:" -ForegroundColor Yellow
    Write-Host "  Stop-Job $($backendJob.Id); Stop-Job $($frontendJob.Id)" -ForegroundColor Yellow
    Write-Host "  Remove-Job $($backendJob.Id); Remove-Job $($frontendJob.Id)" -ForegroundColor Yellow
}
else {
    Write-Host "Uso:" -ForegroundColor White
    Write-Host "  .\start.ps1 -Docker    # Iniciar com Docker" -ForegroundColor Cyan
    Write-Host "  .\start.ps1 -Dev       # Iniciar sem Docker (dev)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Requisitos:" -ForegroundColor White
    Write-Host "  -Docker: Docker + Docker Compose" -ForegroundColor Gray
    Write-Host "  -Dev:    Python 3.11+, Node.js 20+" -ForegroundColor Gray
}
