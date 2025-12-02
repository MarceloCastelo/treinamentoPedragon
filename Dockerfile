# Use Python 3.11 slim como base
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para LDAP, MySQL e Node.js
RUN apt-get update && apt-get install -y \
    gcc \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de configuração do Node.js
COPY package*.json ./

# Instala dependências do Node.js
RUN npm install

# Copia arquivo de requisitos Python
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Compila o CSS do Tailwind para produção
RUN npm run build:css

# Expõe a porta 5000
EXPOSE 5000

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Comando para executar a aplicação
CMD ["python", "-u", "app.py"]
