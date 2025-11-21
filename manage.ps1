# Script para gerenciar ambientes de PRODUÇÃO e DESENVOLVIMENTO
# Uso: .\manage.ps1 [prod|dev] [start|stop|restart|logs|status]

param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet('prod', 'dev')]
    [string]$Environment,
    
    [Parameter(Position=1)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'status', 'both')]
    [string]$Action = 'status'
)

$ErrorActionPreference = "Stop"

function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }

Write-Host ""
Write-Info "=========================================="
Write-Info "  Gerenciador de Ambientes"
Write-Info "=========================================="
Write-Host ""

# Configurações baseadas no ambiente
if ($Environment -eq 'prod') {
    $COMPOSE_FILE = "docker-compose.yml"
    $ENV_FILE = ".env"
    $WEB_PORT = "5000"
    $MYSQL_PORT = "3308"
    $WEB_CONTAINER = "treinamento_adtsa_web"
    $MYSQL_CONTAINER = "treinamento_adtsa_mysql"
    $ENV_NAME = "PRODUÇÃO"
    $COLOR = "Red"
} else {
    $COMPOSE_FILE = "docker-compose.dev.yml"
    $ENV_FILE = ".env.dev"
    $WEB_PORT = "5001"
    $MYSQL_PORT = "3309"
    $WEB_CONTAINER = "treinamento_adtsa_web_dev"
    $MYSQL_CONTAINER = "treinamento_adtsa_mysql_dev"
    $ENV_NAME = "DESENVOLVIMENTO"
    $COLOR = "Green"
}

Write-Host "Ambiente: " -NoNewline
Write-Host $ENV_NAME -ForegroundColor $COLOR
Write-Host ""

# Verifica se o arquivo existe
if (-not (Test-Path $COMPOSE_FILE)) {
    Write-Warning "Arquivo $COMPOSE_FILE não encontrado!"
    exit 1
}

# Executa ação
switch ($Action) {
    'start' {
        Write-Info "🚀 Iniciando ambiente $ENV_NAME..."
        if (Test-Path $ENV_FILE) {
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
        } else {
            docker-compose -f $COMPOSE_FILE up -d
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Success "✅ Ambiente $ENV_NAME iniciado!"
            Write-Host ""
            Write-Host "  • Aplicação: http://localhost:$WEB_PORT" -ForegroundColor White
            Write-Host "  • MySQL:     localhost:$MYSQL_PORT" -ForegroundColor White
        }
    }
    
    'stop' {
        Write-Info "🛑 Parando ambiente $ENV_NAME..."
        docker-compose -f $COMPOSE_FILE down
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Ambiente $ENV_NAME parado!"
        }
    }
    
    'restart' {
        Write-Info "🔄 Reiniciando ambiente $ENV_NAME..."
        docker-compose -f $COMPOSE_FILE down
        Start-Sleep -Seconds 2
        if (Test-Path $ENV_FILE) {
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
        } else {
            docker-compose -f $COMPOSE_FILE up -d
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Ambiente $ENV_NAME reiniciado!"
            Write-Host "  • http://localhost:$WEB_PORT" -ForegroundColor Green
        }
    }
    
    'logs' {
        Write-Info "📋 Logs do ambiente $ENV_NAME (Ctrl+C para sair):"
        Write-Host ""
        docker-compose -f $COMPOSE_FILE logs -f
    }
    
    'status' {
        Write-Info "📊 Status do ambiente $ENV_NAME:"
        Write-Host ""
        docker-compose -f $COMPOSE_FILE ps
        Write-Host ""
        
        $webRunning = docker ps --filter "name=$WEB_CONTAINER" --filter "status=running" -q
        $mysqlRunning = docker ps --filter "name=$MYSQL_CONTAINER" --filter "status=running" -q
        
        if ($webRunning -and $mysqlRunning) {
            Write-Success "✅ Ambiente $ENV_NAME está ATIVO"
            Write-Host "  • Web:   http://localhost:$WEB_PORT" -ForegroundColor Green
            Write-Host "  • MySQL: localhost:$MYSQL_PORT" -ForegroundColor Green
        } else {
            Write-Warning "⚠️  Ambiente $ENV_NAME está INATIVO ou INCOMPLETO"
        }
    }
    
    'both' {
        Write-Info "📊 Status de TODOS os ambientes:"
        Write-Host ""
        Write-Host "═══ PRODUÇÃO ═══" -ForegroundColor Red
        docker ps --filter "name=treinamento_adtsa_web" --filter "name=treinamento_adtsa_mysql" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        Write-Host ""
        Write-Host "═══ DESENVOLVIMENTO ═══" -ForegroundColor Green
        docker ps --filter "name=treinamento_adtsa_web_dev" --filter "name=treinamento_adtsa_mysql_dev" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        Write-Host ""
        
        # Status resumido
        $prodWeb = docker ps --filter "name=treinamento_adtsa_web" --filter "status=running" -q
        $prodMysql = docker ps --filter "name=treinamento_adtsa_mysql" --filter "status=running" -q
        $devWeb = docker ps --filter "name=treinamento_adtsa_web_dev" --filter "status=running" -q
        $devMysql = docker ps --filter "name=treinamento_adtsa_mysql_dev" --filter "status=running" -q
        
        Write-Host "Resumo:" -ForegroundColor Cyan
        if ($prodWeb -and $prodMysql) {
            Write-Host "  • PROD: ✅ ATIVO (http://localhost:5000)" -ForegroundColor Green
        } else {
            Write-Host "  • PROD: ⚠️  INATIVO" -ForegroundColor Yellow
        }
        
        if ($devWeb -and $devMysql) {
            Write-Host "  • DEV:  ✅ ATIVO (http://localhost:5001)" -ForegroundColor Green
        } else {
            Write-Host "  • DEV:  ⚠️  INATIVO" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
