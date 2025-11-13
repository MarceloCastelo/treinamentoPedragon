from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configuração da chave secreta para sessões
    app.secret_key = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento-123')
    
    # Registra o blueprint de autenticação
    from auth.routes import auth_bp, format_video_name
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Registra o filtro personalizado para formatação de nomes
    app.jinja_env.filters['format_video_name'] = format_video_name
    
    # Rota principal - redireciona para login
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Executa em modo debug conforme solicitado
    app.run(debug=True, host='0.0.0.0', port=5000)