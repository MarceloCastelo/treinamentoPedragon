# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import sys

# Garante que o encoding padrão seja UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Carrega variáveis de ambiente
load_dotenv()

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configuração para suportar UTF-8
    app.config['JSON_AS_ASCII'] = False
    
    # Configuração da chave secreta para sessões
    app.secret_key = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento-123')
    
    # Registra os blueprints modularizados
    from routes import auth_bp, video_bp, progress_bp, user_bp, exam_bp, admin_bp
    from routes.video_routes import format_video_name
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(video_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(exam_bp)
    app.register_blueprint(admin_bp)
    
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