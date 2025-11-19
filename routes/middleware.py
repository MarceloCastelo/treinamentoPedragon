"""
Middleware e decorators para autenticação e autorização
"""
from flask import session, redirect, url_for, flash, request
from functools import wraps
from .database import get_user, create_or_update_user, update_session_activity


def login_required(f):
    """Decorator para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        
        # Atualizar atividade da sessão
        if hasattr(session, 'sid'):
            update_session_activity(session.sid)
        
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
                user_data.get('empresa'),
                user_data.get('marca'),
                user_data.get('unidade'),
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
    """Retorna o username do usuário atual (sAMAccountName)"""
    user_data = get_current_user()
    if user_data:
        return user_data.get('sAMAccountName', user_data.get('displayName', ''))
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
