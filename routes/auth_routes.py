"""
Rotas de autenticação (login/logout)
"""
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .ldap_service import authenticate_ldap, is_admin_user
from .database import register_session, remove_session, create_or_update_user

# Criação do blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor, preencha usuário e senha.', 'error')
            return render_template('login.html')
        
        # Tentar autenticar no LDAP
        user_data = authenticate_ldap(username, password)
        
        if user_data:
            # Verificar se é administrador
            is_admin = is_admin_user(user_data)
            
            # Gerar ou recuperar session_id único
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            # Salvar dados do usuário na sessão
            session['user'] = user_data
            session['is_admin'] = is_admin
            
            # Obter informações da requisição
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            username = user_data.get('sAMAccountName', user_data.get('displayName', ''))
            
            # IMPORTANTE: Criar/atualizar usuário ANTES de registrar sessão
            # (devido à foreign key constraint)
            # preserve_existing=True garante que dados do perfil não sejam apagados no login
            # Não passamos os campos extras (empresa, marca, etc) para não sobrescrevê-los
            create_or_update_user(
                username=username,
                email=user_data.get('mail'),
                preserve_existing=True
            )
            
            # Registrar sessão ativa no banco
            register_session(session['session_id'], username, ip_address, user_agent)
            
            flash(f'Bem-vindo, {user_data["displayName"]}!', 'success')
            
            # Redirecionar para dashboard admin se for administrador
            if is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('video.home'))
        else:
            flash('Usuário ou senha inválidos. Tente novamente.', 'error')
            return render_template('login.html')
    
    # GET request - mostrar formulário de login
    # Se já estiver logado, redirecionar para home
    if 'user' in session:
        return redirect(url_for('video.home'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Rota de logout"""
    # Remover sessão do banco de dados
    if 'session_id' in session:
        remove_session(session['session_id'])
    
    # Limpar sessão
    session.pop('user', None)
    session.pop('is_admin', None)
    session.pop('session_id', None)
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('auth.login'))
