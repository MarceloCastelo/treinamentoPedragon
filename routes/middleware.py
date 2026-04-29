"""
Middleware e decorators para autenticação e autorização
"""
import os
from flask import session, redirect, url_for, flash, request
from functools import wraps
from .database import get_user, create_or_update_user, update_session_activity

# Usuário fictício para bypass de autenticação (apenas desenvolvimento)
_BYPASS_USER = {
    'username': 'dev_user',
    'display_name': 'Dev User',
    'email': 'dev@dev.local',
}


def login_required(f):
    """Decorator para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if os.environ.get('BYPASS_AUTH') == '1':
            if 'user' not in session:
                session['user'] = _BYPASS_USER
                session['is_admin'] = False
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        
        # Atualizar atividade da sessão usando o session_id correto
        if 'session_id' in session:
            update_session_activity(session['session_id'])
        
        return f(*args, **kwargs)
    return decorated_function


def profile_complete_required(f):
    """Decorator para exigir que o perfil esteja completo antes de acessar"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        
        # Verificar se as informações adicionais estão preenchidas no banco
        username = get_current_username()
        if username:
            user_data = get_user(username)
            
            # Se não existir ou campos obrigatórios estiverem vazios, redirecionar para o perfil
            if not user_data or not all([
                user_data.get('setor'),
                user_data.get('cargo')
            ]):
                flash('Por favor, complete suas informações adicionais no perfil antes de acessar os vídeos.', 'warning')
                return redirect(url_for('user.profile'))
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Retorna o usuário atual da sessão"""
    return session.get('user')


def get_current_username():
    """Retorna o username do usuário atual"""
    user_data = get_current_user()
    if user_data:
        return user_data.get('username', '')
    return None


def is_admin():
    """Verifica se o usuário atual é administrador"""
    return session.get('is_admin', False)


def admin_required(f):
    """Decorator para proteger rotas que requerem privilégios de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Faça login para acessar esta área.', 'error')
            return redirect(url_for('auth.login'))
        
        if not is_admin():
            flash('Acesso negado. Você não tem permissão de administrador.', 'error')
            return redirect(url_for('video.home'))
        
        return f(*args, **kwargs)
    return decorated_function
