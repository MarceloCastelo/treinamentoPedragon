# Sistema de Backup Automatico

O sistema agora conta com backup automatico diario do banco de dados MySQL.

## Configuracao Rapida

1. **Configurar backup automatico** (executar como Administrador):
   ```powershell
   cd scripts
   .\setup_backup_schedule.ps1
   ```

2. **Testar backup manualmente**:
   ```powershell
   cd scripts
   .\backup_database.ps1
   ```

## Detalhes

- **Localizacao dos backups**: `D:\CTC ADTSA\backups`
- **Frequencia**: Diariamente as 23:00
- **Retencao**: 30 dias
- **Formato**: ZIP com dump SQL completo

## Documentacao Completa

Para mais informacoes, consulte: [`scripts/BACKUP_GUIDE.md`](scripts/BACKUP_GUIDE.md)

## Scripts Disponiveis

- `backup_database.ps1` - Executa backup do banco de dados
- `setup_backup_schedule.ps1` - Configura tarefa agendada do Windows
- `restore_database.ps1` - Restaura um backup existente
