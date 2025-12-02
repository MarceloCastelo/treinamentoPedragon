# Tailwind CSS - Setup e Uso

## Instalação Concluída ✅

O Tailwind CSS foi configurado corretamente para produção neste projeto.

## Estrutura de Arquivos

- `package.json` - Dependências e scripts npm
- `tailwind.config.js` - Configuração do Tailwind CSS
- `static/css/input.css` - Arquivo CSS de entrada com diretivas do Tailwind
- `static/css/output.css` - Arquivo CSS compilado (usado em produção)

## Scripts Disponíveis

### Build para Produção
```bash
npm run build:css
```
Este comando compila e minifica o CSS do Tailwind. Execute sempre que:
- Modificar os templates HTML
- Adicionar novas classes do Tailwind
- Antes de fazer deploy

### Modo de Desenvolvimento (Watch)
```bash
npm run watch:css
```
Este comando fica observando alterações nos arquivos e recompila automaticamente o CSS.

## Workflow de Desenvolvimento

1. **Durante o desenvolvimento:**
   - Abra um terminal e execute: `npm run watch:css`
   - Edite seus templates HTML normalmente
   - O CSS será recompilado automaticamente

2. **Antes de fazer commit/deploy:**
   - Execute: `npm run build:css`
   - Commit o arquivo `static/css/output.css` gerado

## Adicionando Novas Classes Tailwind

1. Edite seus templates HTML em `templates/` ou JavaScript em `static/js/`
2. Use as classes do Tailwind normalmente
3. O Tailwind CLI irá detectar e incluir apenas as classes que você está usando (tree-shaking)

## Customização

Para customizar o Tailwind CSS (cores, fontes, etc.), edite o arquivo `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'custom-blue': '#032B56',
      },
    },
  },
}
```

## Arquivos Ignorados no Git

Os seguintes arquivos/pastas estão no `.gitignore`:
- `node_modules/` - Dependências npm (não fazer commit)
- `package-lock.json` - Lock file do npm

O arquivo `static/css/output.css` **deve** ser commitado, pois é necessário para produção.

## Solução de Problemas

### CSS não está sendo aplicado
1. Verifique se o arquivo `static/css/output.css` existe
2. Execute: `npm run build:css`
3. Limpe o cache do navegador (Ctrl+Shift+R)

### Classes não aparecem
1. Certifique-se de que os paths estão corretos em `tailwind.config.js`
2. Execute: `npm run build:css`
3. Verifique se você salvou o arquivo HTML

### Erro ao executar npm run
1. Certifique-se de que as dependências estão instaladas: `npm install`
2. Verifique se o Node.js está instalado: `node --version`

## Integração com Docker

O Dockerfile foi atualizado para:
1. Instalar Node.js 20.x durante o build da imagem
2. Instalar as dependências npm (`npm install`)
3. Compilar o CSS do Tailwind automaticamente (`npm run build:css`)

### Build da Imagem Docker

Quando você executar `docker-compose build` ou `docker-compose up --build`, o CSS do Tailwind será compilado automaticamente dentro do container.

### Importante para Deploy

- O arquivo `static/css/output.css` **deve** estar no repositório
- Se você modificar os templates, execute `npm run build:css` antes de fazer o build do Docker
- O `.dockerignore` exclui `node_modules/` para otimizar o build (será instalado no container)

