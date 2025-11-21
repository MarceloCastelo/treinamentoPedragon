# Script de gerenciamento do ambiente de DESENVOLVIMENTO
# Uso: .\dev.ps1 [start|stop|restart|logs|status]

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'status', 'rebuild', 'clean')]
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
$DEV_COMPOSE = "docker-compose.dev.yml"
$DEV_ENV = ".env.dev"

Write-Info "=========================================="
Write-Info "  Ambiente de DESENVOLVIMENTO"
Write-Info "  Projeto: $PROJECT_NAME"
Write-Info "=========================================="
Write-Host ""

# Verifica se o arquivo docker-compose.dev.yml existe
if (-not (Test-Path $DEV_COMPOSE)) {
    Write-Error "Arquivo $DEV_COMPOSE não encontrado!"
    exit 1
}

switch ($Action) {
    'start' {
        Write-Info "🚀 Iniciando ambiente de desenvolvimento..."
        docker-compose -f $DEV_COMPOSE --env-file $DEV_ENV up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Success "✅ Ambiente de desenvolvimento iniciado!"
            Write-Host ""
            Write-Info "📋 Informações:"
            Write-Host "  • Aplicação: http://localhost:5001" -ForegroundColor White
            Write-Host "  • MySQL Dev: localhost:3309" -ForegroundColor White
            Write-Host "  • Database:  treinamento_adtsa_dev" -ForegroundColor White
            Write-Host "  • User:      dev_user" -ForegroundColor White
            Write-Host ""
            Write-Info "💡 Comandos úteis:"
            Write-Host "  • Ver logs:     .\dev.ps1 logs" -ForegroundColor White
            Write-Host "  • Parar:        .\dev.ps1 stop" -ForegroundColor White
            Write-Host "  • Reiniciar:    .\dev.ps1 restart" -ForegroundColor White
            Write-Host "  • Status:       .\dev.ps1 status" -ForegroundColor White
        } else {
            Write-Error "❌ Erro ao iniciar ambiente de desenvolvimento"
            exit 1
        }
    }
    
    'stop' {
        Write-Info "🛑 Parando ambiente de desenvolvimento..."
        docker-compose -f $DEV_COMPOSE down
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Ambiente de desenvolvimento parado!"
        } else {
            Write-Error "❌ Erro ao parar ambiente"
            exit 1
        }
    }
    
    'restart' {
        Write-Info "🔄 Reiniciando ambiente de desenvolvimento..."
        docker-compose -f $DEV_COMPOSE down
        Start-Sleep -Seconds 2
        docker-compose -f $DEV_COMPOSE --env-file $DEV_ENV up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Ambiente reiniciado!"
            Write-Host ""
            Write-Info "Aplicação disponível em: http://localhost:5001"
        } else {
            Write-Error "❌ Erro ao reiniciar ambiente"
            exit 1
        }
    }
    
    'logs' {
        Write-Info "📋 Exibindo logs do ambiente de desenvolvimento..."
        Write-Info "Pressione Ctrl+C para sair"
        Write-Host ""
        docker-compose -f $DEV_COMPOSE logs -f
    }
    
    'status' {
        Write-Info "📊 Status do ambiente de desenvolvimento:"
        Write-Host ""
        docker-compose -f $DEV_COMPOSE ps
        Write-Host ""
        
        # Verifica se os containers estão rodando
        $webRunning = docker ps --filter "name=treinamento_adtsa_web_dev" --filter "status=running" -q
        $mysqlRunning = docker ps --filter "name=treinamento_adtsa_mysql_dev" --filter "status=running" -q
        
        if ($webRunning -and $mysqlRunning) {
            Write-Success "✅ Ambiente DEV está RODANDO"
            Write-Host "  • Web:   http://localhost:5001" -ForegroundColor Green
            Write-Host "  • MySQL: localhost:3309" -ForegroundColor Green
        } else {
            Write-Warning "⚠️  Ambiente DEV não está completamente ativo"
            if (-not $webRunning) { Write-Host "  • Container web_dev: PARADO" -ForegroundColor Red }
            if (-not $mysqlRunning) { Write-Host "  • Container mysql_dev: PARADO" -ForegroundColor Red }
        }
    }
    
    'rebuild' {
        Write-Warning "🔨 Reconstruindo imagens do ambiente de desenvolvimento..."
        docker-compose -f $DEV_COMPOSE down
        docker-compose -f $DEV_COMPOSE build --no-cache
        docker-compose -f $DEV_COMPOSE --env-file $DEV_ENV up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Ambiente reconstruído e iniciado!"
            Write-Info "Aplicação disponível em: http://localhost:5001"
        } else {
            Write-Error "❌ Erro ao reconstruir ambiente"
            exit 1
        }
    }
    
    'clean' {
        Write-Warning "🧹 Limpando completamente o ambiente de desenvolvimento..."
        Write-Warning "ATENÇÃO: Isso irá remover TODOS os dados do banco DEV!"
        $confirm = Read-Host "Tem certeza? (digite 'SIM' para confirmar)"
        
        if ($confirm -eq 'SIM') {
            docker-compose -f $DEV_COMPOSE down -v
            Write-Success "✅ Ambiente limpo! Todos os dados foram removidos."
            Write-Info "Use '.\dev.ps1 start' para iniciar novamente"
        } else {
            Write-Info "Operação cancelada."
        }
    }
}

Write-Host ""
