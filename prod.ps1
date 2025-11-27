# Script de gerenciamento do ambiente de PRODUÇÃO
# Uso: .\prod.ps1 [start|stop|restart|logs|status|rebuild|update]

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'status', 'rebuild', 'update')]
    [string]$Action = 'start'
)

$ErrorActionPreference = "Stop"

# Cores para output
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }

# Configurações
$PROJECT_NAME = "treinamento_adtsa"
$COMPOSE_FILE = "docker-compose.yml"

Write-Info "=========================================="
Write-Info "  Ambiente de PRODUÇÃO"
Write-Info "  Projeto: $PROJECT_NAME"
Write-Info "=========================================="
Write-Host ""

# Verifica se o arquivo docker-compose.yml existe
if (-not (Test-Path $COMPOSE_FILE)) {
    Write-Error "Arquivo $COMPOSE_FILE não encontrado!"
    exit 1
}

switch ($Action) {

    'start' {
        Write-Info "Iniciando ambiente de produção..."
        docker-compose -f $COMPOSE_FILE up -d
        Write-Success "Ambiente iniciado!"
        Write-Info "Aplicação disponível em: http://localhost:5000"
    }

    'stop' {
        Write-Info "Parando ambiente..."
        docker-compose -f $COMPOSE_FILE down
        Write-Success "Ambiente parado!"
    }

    'restart' {
        Write-Info "Reiniciando containers..."
        docker-compose -f $COMPOSE_FILE restart
        Write-Success "Containers reiniciados!"
        Write-Info "Aplicação disponível em: http://localhost:5000"
    }

    'logs' {
        Write-Info "Exibindo logs (Ctrl+C para sair)..."
        docker-compose -f $COMPOSE_FILE logs -f
    }

    'status' {
        Write-Info "Status do ambiente:"
        docker-compose -f $COMPOSE_FILE ps
    }

    'rebuild' {
        Write-Warning "Reconstruindo imagens..."
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE build --no-cache
        docker-compose -f $COMPOSE_FILE up -d
        Write-Success "Imagens reconstruídas!"
        Write-Info "Aplicação disponível em: http://localhost:5000"
    }

    'update' {
        Write-Info "Atualizando aplicação após merge..."
        Write-Info "1. Parando containers..."
        docker-compose -f $COMPOSE_FILE down
        
        Write-Info "2. Reconstruindo imagem web com novas mudanças..."
        docker-compose -f $COMPOSE_FILE build web
        
        Write-Info "3. Iniciando containers..."
        docker-compose -f $COMPOSE_FILE up -d
        
        Start-Sleep -Seconds 5
        
        Write-Success "Aplicação atualizada com sucesso!"
        Write-Info "Aplicação disponível em: http://localhost:5000"
        Write-Info ""
        Write-Info "Para verificar os logs: .\prod.ps1 logs"
    }
}

Write-Host ""
exit 0
