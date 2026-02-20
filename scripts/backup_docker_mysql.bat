@echo off
:: ============================================================
::  Backup automatico do MySQL via Docker
::  Projeto: treinamento_adtsa
::  Compativel com Agendador de Tarefas do Windows
:: ============================================================

:: ---------- CONFIGURACOES ----------
set CONTAINER=treinamento_adtsa_mysql
set DB_NAME=treinamento_adtsa
set DB_USER=adtsa_user
set DB_PASS=adtsa_pass123

:: Pasta onde os backups serao salvos
set BACKUP_DIR=E:\Marcelo Castelo\Projetos\treinamento_adtsa\backups

:: Quantos dias de backup manter (0 = manter todos)
set RETENTION_DAYS=30

:: Pasta de logs
set LOG_FILE=%BACKUP_DIR%\backup.log
:: -----------------------------------

:: Cria a pasta de backup se nao existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: Monta o nome do arquivo com data e hora
for /f "tokens=1-3 delims=/" %%a in ("%DATE%") do (
    set DIA=%%a
    set MES=%%b
    set ANO=%%c
)
for /f "tokens=1-2 delims=:." %%a in ("%TIME: =0%") do (
    set HORA=%%a
    set MIN=%%b
)
set TIMESTAMP=%ANO%%MES%%DIA%_%HORA%%MIN%
set BACKUP_FILE=%BACKUP_DIR%\backup_%DB_NAME%_%TIMESTAMP%.sql.gz

:: Registra inicio no log
echo. >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"
echo [%DATE% %TIME%] Iniciando backup do banco: %DB_NAME% >> "%LOG_FILE%"

:: Verifica se o container esta rodando
docker inspect -f "{{.State.Running}}" %CONTAINER% 2>nul | findstr /i "true" >nul
if errorlevel 1 (
    echo [%DATE% %TIME%] ERRO: Container '%CONTAINER%' nao esta em execucao. >> "%LOG_FILE%"
    echo ERRO: Container '%CONTAINER%' nao esta em execucao.
    exit /b 1
)

:: Executa o mysqldump dentro do container e comprime com gzip
docker exec %CONTAINER% sh -c "mysqldump -u%DB_USER% -p%DB_PASS% --single-transaction --routines --triggers --events --hex-blob %DB_NAME% | gzip" > "%BACKUP_FILE%"

if errorlevel 1 (
    echo [%DATE% %TIME%] ERRO: Falha ao gerar o backup. >> "%LOG_FILE%"
    echo ERRO: Falha ao gerar o backup. Verifique o log: %LOG_FILE%
    :: Remove arquivo corrompido se foi criado
    if exist "%BACKUP_FILE%" del "%BACKUP_FILE%"
    exit /b 1
)

:: Verifica se o arquivo tem tamanho > 0
for %%F in ("%BACKUP_FILE%") do set FILE_SIZE=%%~zF
if "%FILE_SIZE%"=="0" (
    echo [%DATE% %TIME%] ERRO: Arquivo de backup vazio (tamanho=0). >> "%LOG_FILE%"
    del "%BACKUP_FILE%"
    exit /b 1
)

echo [%DATE% %TIME%] Backup criado com sucesso: %BACKUP_FILE% (%FILE_SIZE% bytes) >> "%LOG_FILE%"
echo Backup criado: %BACKUP_FILE%

:: Remove backups mais antigos que RETENTION_DAYS dias (se configurado)
if %RETENTION_DAYS% GTR 0 (
    echo [%DATE% %TIME%] Removendo backups com mais de %RETENTION_DAYS% dias... >> "%LOG_FILE%"
    forfiles /p "%BACKUP_DIR%" /s /m backup_%DB_NAME%_*.sql.gz /d -%RETENTION_DAYS% /c "cmd /c del @path" 2>nul
    echo [%DATE% %TIME%] Limpeza de backups antigos concluida. >> "%LOG_FILE%"
)

echo [%DATE% %TIME%] Processo finalizado com sucesso. >> "%LOG_FILE%"
echo Backup concluido com sucesso.
exit /b 0
