# Script para restaurar backup do banco de dados MySQL

param(
    [Parameter(Mandatory=$false)]
    [string]$BackupFile,
    
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "D:\CTC ADTSA\backups"
)

# Configuracoes do banco de dados
$ContainerName = "treinamento_adtsa_mysql"
$DatabaseName = "treinamento_adtsa"
$MySQLUser = "root"
$MySQLPassword = "rootpass123"

Write-Host "=== Restauracao de Backup do Banco de Dados ===" -ForegroundColor Cyan

# Se nao foi especificado um arquivo, listar os disponiveis
if (-not $BackupFile) {
    Write-Host ""
    Write-Host "Backups disponiveis em: $BackupPath" -ForegroundColor Yellow
    
    if (-not (Test-Path $BackupPath)) {
        Write-Host "ERRO: Diretorio de backup nao encontrado: $BackupPath" -ForegroundColor Red
        exit 1
    }
    
    $Backups = Get-ChildItem -Path $BackupPath -Filter "backup_${DatabaseName}_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object @{Name="Nº";Expression={$script:counter++}}, Name, @{Name="Tamanho (MB)";Expression={[math]::Round($_.Length / 1MB, 2)}}, LastWriteTime, FullName
    
    $counter = 1
    $Backups | ForEach-Object { $_.Nº = $counter; $counter++ } | Format-Table Nº, Name, "Tamanho (MB)", LastWriteTime -AutoSize
    
    if (-not $Backups) {
        Write-Host "Nenhum backup encontrado!" -ForegroundColor Red
        exit 1
    }
    
    $Selection = Read-Host "`nDigite o numero do backup para restaurar (ou 'q' para sair)"
    
    if ($Selection -eq 'q') {
        Write-Host "Operacao cancelada." -ForegroundColor Yellow
        exit 0
    }
    
    $SelectedBackup = $Backups | Where-Object { $_.Nº -eq [int]$Selection }
    
    if (-not $SelectedBackup) {
        Write-Host "Selecao invalida!" -ForegroundColor Red
        exit 1
    }
    
    $BackupFile = $SelectedBackup.FullName
}

# Verificar se o arquivo existe
if (-not (Test-Path $BackupFile)) {
    Write-Host "ERRO: Arquivo de backup nao encontrado: $BackupFile" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Arquivo de backup: $BackupFile" -ForegroundColor Cyan

# Verificar se o container esta rodando
$ContainerStatus = docker ps --filter "name=$ContainerName" --format "{{.Status}}"
if (-not $ContainerStatus) {
    Write-Host "ERRO: Container $ContainerName nao esta rodando!" -ForegroundColor Red
    exit 1
}

# Confirmacao
Write-Host ""
Write-Host "ATENCAO: Esta operacao ira substituir todos os dados do banco de dados!" -ForegroundColor Yellow
$Confirm = Read-Host "Deseja continuar? (sim/nao)"

if ($Confirm -ne "sim") {
    Write-Host "Operacao cancelada." -ForegroundColor Yellow
    exit 0
}

# Descompactar se for arquivo .zip
$SqlFile = $BackupFile
$TempFile = $false

if ($BackupFile -like "*.zip") {
    Write-Host ""
    Write-Host "Descompactando backup..." -ForegroundColor Cyan
    $TempDir = Join-Path $env:TEMP "mysql_restore_$(Get-Date -Format 'yyyyMMddHHmmss')"
    New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    
    Expand-Archive -Path $BackupFile -DestinationPath $TempDir -Force
    $SqlFile = Get-ChildItem -Path $TempDir -Filter "*.sql" | Select-Object -First 1 -ExpandProperty FullName
    $TempFile = $true
    
    if (-not $SqlFile) {
        Write-Host "ERRO: Nenhum arquivo .sql encontrado no backup!" -ForegroundColor Red
        Remove-Item $TempDir -Recurse -Force
        exit 1
    }
    
    Write-Host "[OK] Backup descompactado" -ForegroundColor Green
}

# Copiar arquivo SQL para o container
Write-Host ""
Write-Host "Copiando arquivo para o container..." -ForegroundColor Cyan
$ContainerSqlFile = "/tmp/restore_backup.sql"

try {
    docker cp $SqlFile "${ContainerName}:${ContainerSqlFile}"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao copiar arquivo para o container"
    }
    
    Write-Host "[OK] Arquivo copiado para o container" -ForegroundColor Green
    
    # Restaurar o banco de dados
    Write-Host ""
    Write-Host "Restaurando banco de dados..." -ForegroundColor Cyan
    
    $RestoreCommand = "mysql -u$MySQLUser -p$MySQLPassword $DatabaseName < $ContainerSqlFile"
    docker exec $ContainerName bash -c $RestoreCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Banco de dados restaurado com sucesso!" -ForegroundColor Green
    } else {
        throw "Falha ao restaurar o banco de dados"
    }
    
    # Limpar arquivo temporario do container
    docker exec $ContainerName rm $ContainerSqlFile
    
} catch {
    Write-Host ""
    Write-Host "ERRO durante a restauracao:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
} finally {
    # Limpar arquivos temporarios
    if ($TempFile -and (Test-Path $TempDir)) {
        Remove-Item $TempDir -Recurse -Force
    }
}

Write-Host ""
Write-Host "[OK] Processo de restauracao concluido!" -ForegroundColor Green
