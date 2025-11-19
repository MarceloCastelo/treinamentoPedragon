# Guia de Uso do Docker

## 🐳 Como rodar a aplicação no Docker

### Pré-requisitos
- Docker Desktop instalado no Windows
- Docker Compose disponível

### Comandos principais

#### 1. Construir e iniciar os containers
```powershell
docker-compose up --build -d
```

#### 2. Ver logs da aplicação
```powershell
# Logs de todos os serviços
docker-compose logs -f

# Logs apenas da aplicação web
docker-compose logs -f web

# Logs apenas do MySQL
docker-compose logs -f mysql
```

#### 3. Parar os containers
```powershell
docker-compose down
```

#### 4. Parar e remover volumes (apaga dados do banco)
```powershell
docker-compose down -v
```

#### 5. Reiniciar apenas um serviço
```powershell
# Reiniciar aplicação web
docker-compose restart web

# Reiniciar MySQL
docker-compose restart mysql
```

#### 6. Verificar status dos containers
```powershell
docker-compose ps
```

#### 7. Acessar o shell do container
```powershell
# Acessar container da aplicação
docker exec -it treinamento_adtsa_web bash

# Acessar MySQL
docker exec -it treinamento_adtsa_mysql mysql -u adtsa_user -p
```

### Acessar a aplicação

Após iniciar os containers, acesse:
- **Aplicação**: http://localhost:5000
- **MySQL** (via cliente externo): localhost:3308

### Estrutura do Docker

- **Dockerfile**: Define como construir a imagem da aplicação Python/Flask
- **docker-compose.yml**: Orquestra os serviços (web + mysql)
- **.dockerignore**: Arquivos ignorados ao construir a imagem

### Variáveis de Ambiente

As variáveis estão configuradas no `docker-compose.yml`:
- Banco de dados: Conecta no serviço `mysql` (não em `localhost`)
- Porta interna: 3306 (comunicação entre containers)
- Porta externa: 3308 (acesso do host ao MySQL)

### Troubleshooting

#### Container não inicia
```powershell
# Ver logs detalhados
docker-compose logs web

# Reconstruir imagem
docker-compose build --no-cache web
docker-compose up -d
```

#### Erro de conexão com banco
```powershell
# Verificar se MySQL está saudável
docker-compose ps

# Reiniciar MySQL
docker-compose restart mysql

# Aguardar alguns segundos e reiniciar web
docker-compose restart web
```

#### Alterações no código não aparecem
```powershell
# Reconstruir e reiniciar
docker-compose up --build -d
```

#### Resetar tudo
```powershell
# Para containers, remove volumes e recria
docker-compose down -v
docker-compose up --build -d
```

### Desenvolvimento

Para desenvolvimento local com hot-reload, você pode montar volumes adicionais no `docker-compose.yml`:

```yaml
volumes:
  - ./:/app  # Monta todo o código
```

Isso permite que alterações no código sejam refletidas automaticamente (se usar `debug=True` no Flask).
