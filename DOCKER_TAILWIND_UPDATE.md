# Guia de Atualização - Tailwind CSS no Docker

## Mudanças Realizadas

### 1. Dockerfile
- ✅ Instalação do Node.js 20.x
- ✅ Cópia dos arquivos `package.json` e `package-lock.json`
- ✅ Instalação das dependências npm
- ✅ Compilação automática do CSS do Tailwind durante o build

### 2. .dockerignore
- ✅ Adicionado `node_modules/` (será instalado no container)
- ✅ Adicionado `package-lock.json` (será gerado no container)
- ✅ Adicionado scripts de desenvolvimento local

### 3. Novos Arquivos
- ✅ `package.json` - Dependências e scripts npm
- ✅ `tailwind.config.js` - Configuração do Tailwind CSS
- ✅ `static/css/input.css` - Arquivo CSS de entrada
- ✅ `static/css/output.css` - Arquivo CSS compilado
- ✅ `scripts/watch-tailwind.ps1` - Script para desenvolvimento

## Como Fazer o Deploy

### Opção 1: Build Local e Push do CSS
```powershell
# 1. Compile o CSS localmente
npm run build:css

# 2. Commit o arquivo output.css
git add static/css/output.css
git commit -m "Update compiled Tailwind CSS"

# 3. Build e deploy do Docker
docker-compose build
docker-compose up -d
```

### Opção 2: Build Completo no Docker
```powershell
# O Docker irá compilar o CSS automaticamente
docker-compose build
docker-compose up -d
```

## Desenvolvimento Local

### Sem Docker (Recomendado para desenvolvimento)
```powershell
# Terminal 1: Watch do Tailwind CSS
npm run watch:css
# ou
.\scripts\watch-tailwind.ps1

# Terminal 2: Servidor Flask
.\scripts\dev.ps1
```

### Com Docker
```powershell
# Build e start dos containers
docker-compose -f docker-compose.dev.yml up --build

# Para rebuild após mudanças nos templates
docker-compose -f docker-compose.dev.yml build web
docker-compose -f docker-compose.dev.yml up -d
```

## Verificações Importantes

### Antes de Fazer Deploy
- [ ] Execute `npm run build:css` localmente
- [ ] Verifique se `static/css/output.css` existe e está atualizado
- [ ] Commit o arquivo `output.css` no git
- [ ] Teste localmente antes do build do Docker

### Teste do Build Docker
```powershell
# Build da imagem
docker-compose build web

# Verificar se o CSS foi compilado no container
docker run --rm treinamento_adtsa_web ls -lh /app/static/css/

# Deve mostrar o arquivo output.css
```

## Troubleshooting

### Erro: "npm command not found" no Docker
- Verifique se o Node.js está sendo instalado corretamente no Dockerfile
- Execute: `docker-compose build --no-cache web`

### CSS não atualiza no container
1. Recompile localmente: `npm run build:css`
2. Commit: `git add static/css/output.css && git commit -m "Update CSS"`
3. Rebuild: `docker-compose build web`
4. Restart: `docker-compose up -d`

### Build do Docker muito lento
- O Node.js é instalado apenas uma vez (cached)
- Use `.dockerignore` para excluir arquivos desnecessários
- O `npm install` é cached enquanto o `package.json` não mudar

## Tamanho da Imagem

Adição aproximada de tamanho:
- Node.js: ~50MB
- Dependências npm (Tailwind): ~10MB
- Total: ~60MB adicionais

A imagem final continuará otimizada pois usa multi-stage building pattern.
