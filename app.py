# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import sys
import logging

# Configura encoding no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Carrega variáveis de ambiente
load_dotenv()


def configure_logging():
    """Configura logging global para reduzir verbosidade."""
    
    # Formato padrão dos logs
    logging.basicConfig(
        level=logging.INFO,  # mostra apenas INFO, WARNING, ERROR e CRITICAL
        format='[%(asctime)s] %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # loga no console
        ]
    )

    # Reduz logs de acesso do Werkzeug
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # Opcionalmente suprime logs de libs grandes
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)



def create_app():
    """Factory function para criar a aplicação Flask"""

    app = Flask(__name__)

    # Config UTF-8
    app.config['JSON_AS_ASCII'] = False

    # Configura chave secreta
    app.secret_key = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento-123')

    # Configura logging
    configure_logging()

    # Importa blueprints
    from routes import auth_bp, video_bp, progress_bp, user_bp, exam_bp, admin_bp
    from routes.video_routes import format_video_name
    
    # Registra rotas
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(video_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(exam_bp)
    app.register_blueprint(admin_bp)

    # Adiciona filtro Jinja
    app.jinja_env.filters['format_video_name'] = format_video_name

    # Rota inicial
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app



if __name__ == '__main__':
    app = create_app()

    # Executa servidor com reload automático no ambiente de desenvolvimento
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(
        debug=debug_mode,
        use_reloader=True,
        host='0.0.0.0',
        port=5000,
        extra_files=None
    )
