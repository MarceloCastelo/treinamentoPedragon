# 🚀 Ambiente de Desenvolvimento

Este guia explica como configurar e usar o ambiente de desenvolvimento isolado, permitindo que você trabalhe em outro computador sem afetar o servidor principal de produção.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Diferenças entre DEV e PRODUÇÃO](#diferenças-entre-dev-e-produção)
- [Pré-requisitos](#pré-requisitos)
- [Instalação Inicial](#instalação-inicial)
- [Como Usar](#como-usar)
- [Desenvolvendo com Hot Reload](#desenvolvendo-com-hot-reload)
- [Acesso ao Banco de Dados](#acesso-ao-banco-de-dados)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O ambiente de desenvolvimento é uma **cópia isolada** do ambiente de produção que roda em:
- **Portas diferentes** (para não conflitar)
- **Banco de dados separado** (seus testes não afetam produção)
- **Hot reload ativo** (mudanças no código são aplicadas automaticamente)

### Arquitetura

```
PRODUÇÃO                          DESENVOLVIMENTO
┌─────────────────────┐          ┌─────────────────────┐
│ Web: localhost:5000 │          │ Web: localhost:5001 │
│ MySQL: :3308        │          │ MySQL: :3309        │
│ DB: treinamento_    │          │ DB: treinamento_    │
│     adtsa           │          │     adtsa_dev       │
└─────────────────────┘          └─────────────────────┘
```

---

## 🔄 Diferenças entre DEV e PRODUÇÃO

| Aspecto | PRODUÇÃO | DESENVOLVIMENTO |
|---------|----------|-----------------|
| **Porta Web** | 5000 | 5001 |
| **Porta MySQL** | 3308 | 3309 |
| **Container Web** | `treinamento_adtsa_web` | `treinamento_adtsa_web_dev` |
| **Container MySQL** | `treinamento_adtsa_mysql` | `treinamento_adtsa_mysql_dev` |
| **Banco de Dados** | `treinamento_adtsa` | `treinamento_adtsa_dev` |
| **Usuário DB** | `adtsa_user` | `dev_user` |
| **Senha DB** | `adtsa_pass123` | `dev_pass` |
| **Flask Debug** | Desligado | Ligado |
| **Hot Reload** | Não | Sim |
| **Volume de Código** | Apenas static/templates | Todo código fonte |

---

## 📦 Pré-requisitos

1. **Docker Desktop** instalado e rodando
2. **PowerShell** (versão 5.1 ou superior)
3. **Código fonte** clonado na máquina de desenvolvimento

---

## 🛠️ Instalação Inicial

### 1. Clone o Repositório (se ainda não tiver)

```powershell
cd C:\Users\adtsa\Documents\Marcelo Castelo\Projetos
git clone <URL_DO_REPOSITORIO> treinamento_adtsa_dev
cd treinamento_adtsa_dev
```

### 2. Verifique os Arquivos de Configuração

Certifique-se de que estes arquivos existem:
- ✅ `docker-compose.dev.yml`
- ✅ `.env.dev`
- ✅ `dev.ps1`

### 3. Configure o Caminho dos Vídeos (se necessário)

Edite o `docker-compose.dev.yml` e ajuste o caminho dos vídeos:

```yaml
volumes:
  - C:\Users\SEU_USUARIO\Videos\Treinamento - Dealernet:/app/videos
```

### 4. Inicie o Ambiente

```powershell
.\dev.ps1 start
```

Aguarde alguns segundos até que apareça:
```
✅ Ambiente de desenvolvimento iniciado!
📋 Informações:
  • Aplicação: http://localhost:5001
  • MySQL Dev: localhost:3309
```

---

## 🎮 Como Usar

### Comandos Disponíveis

```powershell
# Iniciar o ambiente de desenvolvimento
.\dev.ps1 start

# Parar o ambiente
.\dev.ps1 stop

# Reiniciar (útil após mudanças grandes)
.\dev.ps1 restart

# Ver logs em tempo real
.\dev.ps1 logs

# Verificar status dos containers
.\dev.ps1 status

# Reconstruir imagens do zero
.\dev.ps1 rebuild

# Limpar tudo (CUIDADO: apaga banco de dados DEV)
.\dev.ps1 clean
```

### Acessando a Aplicação

Depois de iniciar, acesse:
- **Interface Web**: http://localhost:5001
- **Banco de Dados**: localhost:3309

---

## 🔥 Desenvolvendo com Hot Reload

O ambiente de desenvolvimento tem **hot reload** ativado. Isso significa:

### ✅ Mudanças Automáticas (não precisa reiniciar)

- Editar arquivos `.py` em `routes/`
- Modificar `app.py`
- Atualizar templates HTML em `templates/`
- Alterar arquivos CSS/JS em `static/`

**Exemplo:**

1. Edite `routes/user_routes.py`
2. Salve o arquivo (Ctrl+S)
3. Recarregue a página no navegador (F5)
4. ✅ Mudanças aplicadas!

### ⚠️ Precisa Reiniciar

- Mudanças em `requirements.txt`
- Alterações no `Dockerfile`
- Modificações em `docker-compose.dev.yml`

**Como reiniciar:**
```powershell
.\dev.ps1 restart
```

### 📝 Testando Mudanças

```powershell
# 1. Edite o código
# 2. Verifique os logs em tempo real
.\dev.ps1 logs

# 3. Se der erro, reinicie
.\dev.ps1 restart
```

---

## 🗄️ Acesso ao Banco de Dados

### Informações de Conexão

```
Host:     localhost
Port:     3309
Database: treinamento_adtsa_dev
User:     dev_user
Password: dev_pass
```

### Via MySQL Workbench

1. Abra o MySQL Workbench
2. Crie nova conexão:
   - Connection Name: `Treinamento DEV`
   - Hostname: `localhost`
   - Port: `3309`
   - Username: `dev_user`
   - Password: `dev_pass`

### Via Linha de Comando

```powershell
# Acessar MySQL dentro do container
docker exec -it treinamento_adtsa_mysql_dev mysql -u dev_user -pdev_pass treinamento_adtsa_dev
```

### Resetar Banco de Dados

Se precisar começar do zero:

```powershell
# CUIDADO: Isso apaga todos os dados de desenvolvimento!
.\dev.ps1 clean
.\dev.ps1 start
```

---

## 🐛 Troubleshooting

### Problema: Porta 5001 já está em uso

**Solução:** Mude a porta no `docker-compose.dev.yml`:

```yaml
ports:
  - "5002:5000"  # Use 5002 ou outra porta livre
```

### Problema: Erro "Cannot connect to Docker daemon"

**Solução:**
1. Abra o Docker Desktop
2. Aguarde até que o ícone fique verde
3. Tente novamente: `.\dev.ps1 start`

### Problema: Container não inicia (fica reiniciando)

**Solução:** Verifique os logs:

```powershell
.\dev.ps1 logs
```

Procure por erros de:
- Conexão com banco de dados
- Arquivos faltando
- Erros de sintaxe no código

### Problema: Mudanças não aparecem (hot reload não funciona)

**Verificações:**

1. Os volumes estão montados corretamente?
```powershell
docker exec -it treinamento_adtsa_web_dev ls -la /app
```

2. Flask está em modo debug?
```powershell
docker exec -it treinamento_adtsa_web_dev env | grep FLASK
```
Deve mostrar: `FLASK_DEBUG=1`

3. Tente reiniciar:
```powershell
.\dev.ps1 restart
```

### Problema: Vídeos não aparecem

**Solução:** Verifique o caminho no `docker-compose.dev.yml`:

```yaml
volumes:
  - C:\Users\adtsa\Videos\Treinamento - Dealernet:/app/videos
```

Teste se os vídeos estão visíveis:
```powershell
docker exec -it treinamento_adtsa_web_dev ls -la /app/videos
```

### Problema: Preciso limpar tudo e começar do zero

```powershell
# Para tudo
.\dev.ps1 stop

# Remove volumes (apaga banco de dados)
docker-compose -f docker-compose.dev.yml down -v

# Remove imagens
docker rmi treinamento_adtsa-web_dev

# Reconstruir
.\dev.ps1 rebuild
```

---

## 📞 Trabalhando de Outro Computador

### 1. Configuração Inicial

```powershell
# Clone o repositório
git clone <URL> treinamento_adtsa_dev
cd treinamento_adtsa_dev

# Configure o caminho dos vídeos no docker-compose.dev.yml
# Ajuste para o caminho correto no seu computador

# Inicie o ambiente
.\dev.ps1 start
```

### 2. Sincronizando Código com Git

```powershell
# Sempre antes de começar a trabalhar
git pull origin dev

# Faça suas mudanças...
# Edite arquivos, teste localmente em http://localhost:5001

# Quando terminar
git add .
git commit -m "Descrição das mudanças"
git push origin dev
```

### 3. Boas Práticas

✅ **SEMPRE** trabalhe no ambiente DEV primeiro
✅ **TESTE** todas as mudanças localmente
✅ **USE** branches para features grandes
✅ **NUNCA** conecte no banco de produção diretamente
✅ **DOCUMENTE** mudanças importantes

---

## 🎯 Workflow Recomendado

```
1. Iniciar DEV
   .\dev.ps1 start

2. Fazer mudanças no código
   Editar arquivos .py, .html, .css, etc.

3. Testar localmente
   http://localhost:5001

4. Ver logs se necessário
   .\dev.ps1 logs

5. Commit no Git
   git add . && git commit -m "..." && git push

6. Parar DEV quando terminar
   .\dev.ps1 stop
```

---

## 📚 Arquivos de Configuração

### `.env.dev` (Variáveis de Ambiente)

Contém todas as configurações do ambiente de desenvolvimento:
- Credenciais do banco de dados
- Configurações LDAP
- Chave secreta do Flask
- Modo debug

### `docker-compose.dev.yml` (Orquestração)

Define:
- Containers (web e mysql)
- Portas
- Volumes (montagem de código)
- Networks
- Dependências

### `dev.ps1` (Script de Gerenciamento)

Script PowerShell para facilitar operações comuns:
- Start/Stop/Restart
- Ver logs
- Verificar status
- Rebuild
- Clean

---

## 🔐 Segurança

### ⚠️ IMPORTANTE

- **NUNCA** comite o arquivo `.env.dev` com senhas reais
- Use senhas simples **APENAS** em desenvolvimento
- **NUNCA** exponha a porta 5001 para a internet
- O ambiente DEV é **APENAS** para uso local

### Checklist de Segurança

- [ ] Senhas de desenvolvimento são diferentes de produção
- [ ] Arquivo `.env` está no `.gitignore`
- [ ] Portas não estão expostas publicamente
- [ ] Dados sensíveis não estão commitados

---

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os logs**: `.\dev.ps1 logs`
2. **Verifique o status**: `.\dev.ps1 status`
3. **Tente reiniciar**: `.\dev.ps1 restart`
4. **Em último caso**: `.\dev.ps1 clean` e `.\dev.ps1 start`

---

## 📝 Resumo Rápido

```powershell
# Começar a trabalhar
.\dev.ps1 start
# Acesse: http://localhost:5001

# Edite o código normalmente
# As mudanças aparecem automaticamente!

# Ver o que está acontecendo
.\dev.ps1 logs

# Terminar o dia
.\dev.ps1 stop
```

**Pronto! Agora você tem um ambiente de desenvolvimento completo e isolado! 🎉**
