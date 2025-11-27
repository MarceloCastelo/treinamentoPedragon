# Script de Backup do Banco de Dados MySQL
# Executa backup diario do banco de dados treinamento_adtsa

param(
    [string]$BackupPath = "D:\CTC ADTSA\backups",
    [int]$RetentionDays = 30
)

# Configuracoes do banco de dados
$ContainerName = "treinamento_adtsa_mysql"
$DatabaseName = "treinamento_adtsa"
$MySQLUser = "root"
$MySQLPassword = "rootpass123"

# Criar diretorio de backup se nao existir
if (-not (Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    Write-Host "Diretorio de backup criado: $BackupPath"
}

# Nome do arquivo de backup com timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFileName = "backup_${DatabaseName}_${Timestamp}.sql"
$BackupFile = Join-Path $BackupPath $BackupFileName

# Verificar se o container esta rodando
$ContainerStatus = docker ps --filter "name=$ContainerName" --format "{{.Status}}"
if (-not $ContainerStatus) {
    Write-Host "ERRO: Container $ContainerName nao esta rodando!" -ForegroundColor Red
    exit 1
}

Write-Host "Iniciando backup do banco de dados..." -ForegroundColor Cyan
Write-Host "Container: $ContainerName"
Write-Host "Database: $DatabaseName"
Write-Host "Arquivo: $BackupFile"

# Executar mysqldump dentro do container
try {
    $Command = "docker exec $ContainerName mysqldump -u$MySQLUser -p$MySQLPassword --single-transaction --routines --triggers --events $DatabaseName"
    
    # Executar o comando e salvar o resultado
    $BackupContent = Invoke-Expression $Command 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO ao executar mysqldump:" -ForegroundColor Red
        Write-Host $BackupContent
        exit 1
    }
    
    $BackupContent | Out-File -FilePath $BackupFile -Encoding UTF8
    
    # Verificar se o arquivo foi criado e tem conteudo
    if (-not (Test-Path $BackupFile)) {
        Write-Host "ERRO: Arquivo de backup nao foi criado!" -ForegroundColor Red
        exit 1
    }
    
    $FileSize = (Get-Item $BackupFile).Length
    $FileSizeMB = [math]::Round($FileSize / 1MB, 2)
    
    Write-Host "[OK] Backup concluido com sucesso!" -ForegroundColor Green
    Write-Host "  Tamanho: $FileSizeMB MB"
    Write-Host "  Local: $BackupFile"
    
    # Comprimir o backup
    $ZipFile = "$BackupFile.zip"
    Compress-Archive -Path $BackupFile -DestinationPath $ZipFile -Force
    
    if (Test-Path $ZipFile) {
        $ZipSize = (Get-Item $ZipFile).Length
        $ZipSizeMB = [math]::Round($ZipSize / 1MB, 2)
        Write-Host "[OK] Backup comprimido: $ZipSizeMB MB" -ForegroundColor Green
        
        # Remover arquivo SQL nao comprimido
        Remove-Item $BackupFile -Force
    }
} catch {
    Write-Host "ERRO durante o backup:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# Limpeza de backups antigos
Write-Host ""
Write-Host "Limpando backups antigos (mais de $RetentionDays dias)..." -ForegroundColor Cyan
$CutoffDate = (Get-Date).AddDays(-$RetentionDays)
$OldBackups = Get-ChildItem -Path $BackupPath -Filter "backup_${DatabaseName}_*.zip" | Where-Object { $_.LastWriteTime -lt $CutoffDate }

if ($OldBackups) {
    $OldBackups | ForEach-Object {
        Write-Host "  Removendo: $($_.Name)" -ForegroundColor Yellow
        Remove-Item $_.FullName -Force
    }
    Write-Host "[OK] Limpeza concluida. $($OldBackups.Count) backup(s) removido(s)." -ForegroundColor Green
} else {
    Write-Host "  Nenhum backup antigo para remover." -ForegroundColor Gray
}

# Listar backups existentes
Write-Host ""
Write-Host "Backups existentes:" -ForegroundColor Cyan
$ExistingBackups = Get-ChildItem -Path $BackupPath -Filter "backup_${DatabaseName}_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object Name, @{Name="Tamanho (MB)";Expression={[math]::Round($_.Length / 1MB, 2)}}, LastWriteTime

$ExistingBackups | Format-Table -AutoSize

Write-Host ""
Write-Host "[OK] Processo de backup concluido!" -ForegroundColor Green
