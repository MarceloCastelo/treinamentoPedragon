# Script de gerenciamento do ambiente de DESENVOLVIMENTO
# Uso: .\dev.ps1 [start|stop|restart|logs|status]

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'status', 'rebuild', 'clean')]
    [string]$Action = 'start'
)

$ErrorActionPreference = "Stop"

# Define variável de ambiente VIDEOS_DIR para o caminho dinâmico do usuário atual
$env:VIDEOS_DIR = "$env:USERPROFILE\Videos\Treinamento - Dealernet"

# Cores para output
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }

# Configurações
$PROJECT_NAME = "treinamento_adtsa"
$DEV_COMPOSE = "docker-compose.dev.yml"
$DEV_ENV = ".env.dev"

Write-Info "=========================================="
Write-Info "  Ambiente de DESENVOLVIMENTO"
Write-Info "  Projeto: $PROJECT_NAME"
Write-Info "=========================================="
Write-Host ""

# Verifica se o arquivo docker-compose.dev.yml existe
if (-not (Test-Path $DEV_COMPOSE)) {
    Write-Error "Arquivo $DEV_COMPOSE nao encontrado!"
    exit 1
}

switch ($Action) {

    'start' {
        Write-Info "Iniciando ambiente de desenvolvimento..."
        docker-compose -f $DEV_COMPOSE --env-file $DEV_ENV up -d
        Write-Success "Ambiente iniciado!"
    }

    'stop' {
        Write-Info "Parando ambiente..."
        docker-compose -f $DEV_COMPOSE down
        Write-Success "Ambiente parado!"
    }

    'restart' {
        Write-Info "Reiniciando..."
        docker-compose -f $DEV_COMPOSE down
        Start-Sleep -Seconds 2
        docker-compose -f $DEV_COMPOSE --env-file $DEV_ENV up -d
        Write-Success "Ambiente reiniciado!"
    }

    'logs' {
        Write-Info "Exibindo logs (Ctrl+C para sair)..."
        docker-compose -f $DEV_COMPOSE logs -f
    }

    'status' {
        Write-Info "Status do ambiente:"
        docker-compose -f $DEV_COMPOSE ps
    }

    'rebuild' {
        Write-Warning "Reconstruindo imagens..."
        docker-compose -f $DEV_COMPOSE down
        docker-compose -f $DEV_COMPOSE build --no-cache
        docker-compose -f $DEV_COMPOSE --env-file $DEV_ENV up -d
        Write-Success "Imagens reconstruidas!"
    }

    'clean' {
        Write-Warning "Limpando ambiente DEV (dados serao excluidos!)"
        $confirm = Read-Host "Digite 'SIM' para confirmar"
        
        if ($confirm -eq 'SIM') {
            docker-compose -f $DEV_COMPOSE down -v
            Write-Success "Ambiente limpo!"
        } else {
            Write-Info "Cancelado"
        }
    }
}

Write-Host ""
exit 0
