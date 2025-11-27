# Script para configurar tarefa agendada de backup diario
# Execute este script como Administrador

$TaskName = "Backup Diario MySQL - Treinamento ADTSA"
$ScriptPath = Join-Path $PSScriptRoot "backup_database.ps1"
$BackupTime = "23:00"  # Horario do backup (23:00 = 11:00 PM)

Write-Host "Configurando tarefa agendada de backup..." -ForegroundColor Cyan
Write-Host "Nome da tarefa: $TaskName"
Write-Host "Script: $ScriptPath"
Write-Host "Horario: $BackupTime diariamente"

# Verificar se o script existe
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERRO: Script de backup nao encontrado em: $ScriptPath" -ForegroundColor Red
    exit 1
}

# Remover tarefa existente se houver
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Removendo tarefa agendada existente..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Criar acao da tarefa
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

# Criar gatilho diario
$Trigger = New-ScheduledTaskTrigger -Daily -At $BackupTime

# Configuracoes da tarefa
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Criar descricao
$Description = "Backup automatico diario do banco de dados MySQL (treinamento_adtsa). O backup e salvo em D:\CTC ADTSA\backups e mantem os ultimos 30 dias."

# Registrar a tarefa (executar com o usuario atual)
try {
    $Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description $Description -Force | Out-Null
    
    Write-Host ""
    Write-Host "[OK] Tarefa agendada criada com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalhes da tarefa:"
    Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, Date
    
    Write-Host ""
    Write-Host "Proximas execucoes:"
    $Task = Get-ScheduledTask -TaskName $TaskName
    $Task.Triggers | ForEach-Object {
        $Time = ([DateTime]$_.StartBoundary).ToString("HH:mm")
        Write-Host "  - Diariamente as $Time"
    }
    
    Write-Host ""
    Write-Host "Comandos uteis:" -ForegroundColor Cyan
    Write-Host "  Ver tarefa agendada: Get-ScheduledTask -TaskName '$TaskName'"
    Write-Host "  Executar manualmente: Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host "  Ver historico: Get-ScheduledTaskInfo -TaskName '$TaskName'"
    Write-Host "  Remover tarefa: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
    
} catch {
    Write-Host ""
    Write-Host "ERRO ao criar tarefa agendada:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "Tente executar este script como Administrador." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[OK] Configuracao concluida!" -ForegroundColor Green
Write-Host ""
Write-Host "O backup sera executado automaticamente todos os dias as $BackupTime"
Write-Host "Os backups serao salvos em: D:\CTC ADTSA\backups"
Write-Host ""
Write-Host "Voce pode testar o backup agora executando:"
Write-Host "  .\backup_database.ps1" -ForegroundColor Yellow
