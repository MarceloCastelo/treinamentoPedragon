"""
Rotas de autenticação (login/logout)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .ldap_service import authenticate_ldap, is_admin_user

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
            
            # Salvar dados do usuário na sessão
            session['user'] = user_data
            session['is_admin'] = is_admin
            
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
    # Limpar sessão
    session.pop('user', None)
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('auth.login'))
