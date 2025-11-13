# Sistema ADTSA - Autenticação Flask com Active Directory

Esta é uma aplicação Flask que implementa autenticação contra o Active Directory usando LDAP3.

## 🚀 Funcionalidades

- ✅ Login com credenciais do Active Directory
- ✅ Tela de login responsiva e moderna
- ✅ Página inicial protegida com informações do usuário
- ✅ Gerenciamento de sessões Flask
- ✅ Sistema de logout
- ✅ Organização com Blueprints
- ✅ Interface amigável com mensagens de feedback

## 📁 Estrutura do Projeto

```
treinamento_adtsa/
├── app.py                 # Ponto de entrada principal
├── requirements.txt       # Dependências do projeto
├── .env                  # Variáveis de ambiente (configure!)
├── auth/
│   ├── __init__.py       # Pacote de autenticação
│   └── routes.py         # Rotas e lógica LDAP
└── templates/
    ├── login.html        # Página de login
    └── home.html         # Página inicial protegida
```

## ⚙️ Instalação e Configuração

### 1. Instalar Dependências

```powershell
# Criar ambiente virtual (recomendado)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Edite o arquivo `.env` com as configurações do seu Active Directory:

```env
# Endereço do servidor LDAP (Domain Controller)
LDAP_SERVER=ldap://192.168.1.10

# Domínio do Active Directory  
LDAP_DOMAIN=empresa.local

# Base de pesquisa no AD
LDAP_SEARCH_BASE=DC=empresa,DC=local

# Chave secreta para sessões
SECRET_KEY=chave-secreta-unica-aqui
```

**Exemplos de configuração:**

- **LDAP_SERVER**: `ldap://dc01.empresa.com.br`, `192.168.1.10`, `dc01.empresa.local`
- **LDAP_DOMAIN**: `empresa.local`, `empresa.com.br`, `meudominio.local`  
- **LDAP_SEARCH_BASE**: `DC=empresa,DC=local`, `OU=Usuarios,DC=empresa,DC=local`

### 3. Executar a Aplicação

```powershell
python app.py
```

A aplicação estará disponível em: **http://127.0.0.1:5000**

## 🔐 Como Usar

1. **Acesse** http://127.0.0.1:5000
2. **Faça login** com suas credenciais do Active Directory:
   - **Usuário**: seu nome de usuário do AD (sAMAccountName)
   - **Senha**: sua senha do AD
3. **Seja redirecionado** para a página inicial com suas informações
4. **Faça logout** quando necessário

## 📋 Informações Coletadas do AD

A aplicação busca os seguintes atributos do usuário no Active Directory:

- **displayName**: Nome de exibição completo
- **sAMAccountName**: Nome de usuário (login)
- **mail**: Endereço de email

## 🔧 Detalhes Técnicos

### Autenticação LDAP

- Usa **ldap3** com autenticação NTLM
- Formato de usuário: `usuario@dominio.local`
- Busca atributos específicos após autenticação bem-sucedida
- Armazena informações na sessão Flask

### Segurança

- Decorator `@login_required` protege rotas
- Sessões Flask com chave secreta
- Limpeza de sessão no logout
- Validação de entrada nos formulários

### Organização do Código

- **Blueprint** `auth` para separar lógica de autenticação
- **Templates** Jinja2 responsivos
- **Variáveis de ambiente** para configurações sensíveis
- **Tratamento de erros** com mensagens flash

## 🐛 Troubleshooting

### Erro de Conexão LDAP
- Verifique se o servidor LDAP está acessível
- Confirme as configurações de rede e firewall
- Teste conectividade: `telnet servidor_ldap 389`

### Erro de Autenticação
- Verifique usuário e senha
- Confirme o formato do domínio
- Teste com ferramenta LDAP externa

### Erro de Pesquisa de Usuário
- Verifique o `LDAP_SEARCH_BASE`
- Confirme permissões de pesquisa no AD
- Teste com DN específico do usuário

## 📝 Logs

Para debug, os erros LDAP são impressos no console. Para produção, configure logging adequado.

---

**Desenvolvido para treinamento ADTSA - 2025**