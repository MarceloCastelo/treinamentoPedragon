# Sistema de Backup do Banco de Dados

Este sistema realiza backups automaticos diarios do banco de dados MySQL do sistema de treinamento ADTSA.

## Localizacao dos Backups

Os backups sao salvos em: **`D:\CTC ADTSA\backups`**

## Arquivos do Sistema

Todos os scripts estao localizados em: **`scripts/`**

- **`backup_database.ps1`** - Script que executa o backup
- **`setup_backup_schedule.ps1`** - Configura a tarefa agendada
- **`restore_database.ps1`** - Restaura um backup

## Configuracao Inicial

### 1. Configurar o Backup Automatico

Execute como **Administrador**:

```powershell
cd scripts
.\setup_backup_schedule.ps1
```

Isso ira:
- Criar uma tarefa agendada no Windows
- Configurar backup diario as 23:00 (11:00 PM)
- Manter os ultimos 30 dias de backups

### 2. Testar o Backup Manualmente

```powershell
cd scripts
.\backup_database.ps1
```

## Personalizacao

### Alterar Horario do Backup

Edite o arquivo `setup_backup_schedule.ps1` e modifique a linha:

```powershell
$BackupTime = "23:00"  # Altere para o horario desejado
```

Depois execute novamente:

```powershell
cd scripts
.\setup_backup_schedule.ps1
```

### Alterar Retencao de Backups

Por padrao, os backups sao mantidos por 30 dias. Para alterar:

```powershell
cd scripts
.\backup_database.ps1 -RetentionDays 60  # Mantem por 60 dias
```

Ou edite o script e altere o parametro padrao.

### Alterar Local dos Backups

```powershell
cd scripts
.\backup_database.ps1 -BackupPath "E:\MeuLocal\Backups"
```

## Restaurar um Backup

### Modo Interativo (Recomendado)

```powershell
cd scripts
.\restore_database.ps1
```

O script ira:
1. Listar todos os backups disponiveis
2. Permitir escolher qual backup restaurar
3. Solicitar confirmacao antes de restaurar

### Especificar Arquivo Diretamente

```powershell
cd scripts
.\restore_database.ps1 -BackupFile "D:\CTC ADTSA\backups\backup_treinamento_adtsa_20241127_230000.zip"
```

## Gerenciar Tarefa Agendada

### Ver Status da Tarefa

```powershell
Get-ScheduledTask -TaskName "Backup Diario MySQL - Treinamento ADTSA"
```

### Executar Backup Manualmente via Tarefa

```powershell
Start-ScheduledTask -TaskName "Backup Diario MySQL - Treinamento ADTSA"
```

### Ver Historico de Execucoes

```powershell
Get-ScheduledTaskInfo -TaskName "Backup Diario MySQL - Treinamento ADTSA"
```

### Desabilitar Backup Automatico

```powershell
Disable-ScheduledTask -TaskName "Backup Diario MySQL - Treinamento ADTSA"
```

### Habilitar Backup Automatico

```powershell
Enable-ScheduledTask -TaskName "Backup Diario MySQL - Treinamento ADTSA"
```

### Remover Tarefa Agendada

```powershell
Unregister-ScheduledTask -TaskName "Backup Diario MySQL - Treinamento ADTSA" -Confirm:$false
```

## Formato dos Backups

- **Nome**: `backup_treinamento_adtsa_YYYYMMDD_HHMMSS.zip`
- **Formato**: ZIP contendo arquivo SQL
- **Conteudo**: Dump completo do banco de dados incluindo:
  - Estrutura das tabelas
  - Dados
  - Stored procedures, triggers e events

## Importante

1. **Espaco em Disco**: Verifique periodicamente se ha espaco suficiente em `D:\CTC ADTSA\backups`
2. **Container**: O container MySQL deve estar rodando para fazer backup ou restauracao
3. **Permissoes**: O script de configuracao requer privilegios de administrador
4. **Retencao**: Backups mais antigos que 30 dias sao automaticamente removidos

## Verificar Backup

Para verificar se um backup esta integro:

```powershell
# Descompactar manualmente e verificar o arquivo SQL
Expand-Archive -Path "D:\CTC ADTSA\backups\backup_treinamento_adtsa_20241127_230000.zip" -DestinationPath "temp"
Get-Content "temp\backup_treinamento_adtsa_20241127_230000.sql" -First 10
```

## Solucao de Problemas

### Backup nao esta sendo executado

1. Verifique se a tarefa esta habilitada:
   ```powershell
   Get-ScheduledTask -TaskName "Backup Diario MySQL - Treinamento ADTSA"
   ```

2. Verifique o historico de execucao:
   ```powershell
   Get-ScheduledTaskInfo -TaskName "Backup Diario MySQL - Treinamento ADTSA"
   ```

3. Execute manualmente para ver erros:
   ```powershell
   cd scripts
   .\backup_database.ps1
   ```

### Container nao esta rodando

```powershell
# Verificar status
docker ps -a --filter "name=treinamento_adtsa_mysql"

# Iniciar container
.\prod.ps1 start
```

### Erro de permissao ao restaurar

Execute o PowerShell como Administrador.

## Credenciais

As credenciais do banco de dados estao configuradas nos scripts:
- **Usuario**: root
- **Senha**: rootpass123
- **Database**: treinamento_adtsa

Se as credenciais forem alteradas, atualize os scripts correspondentes.
