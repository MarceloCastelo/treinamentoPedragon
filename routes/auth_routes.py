"""
Rotas de autenticação (login/cadastro/logout) — autenticação local
"""
import os
import re
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .database import (
    register_session, remove_session,
    create_or_update_user, get_user, get_user_by_email,
    get_user_by_cpf, create_local_user
)

# Criação do blueprint
auth_bp = Blueprint('auth', __name__)

ALLOWED_DOMAIN = '@pedragon.com.br'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _email_allowed(email: str) -> bool:
    """Verifica se o e-mail pertence ao domínio corporativo permitido."""
    return email.lower().strip().endswith(ALLOWED_DOMAIN)


def _email_to_username(email: str) -> str:
    """Deriva o username a partir do e-mail (parte antes do @)."""
    return email.lower().strip().split('@')[0]


def _format_cpf(cpf: str) -> str:
    """Formata CPF para o padrão 000.000.000-00."""
    digits = ''.join(filter(str.isdigit, cpf))
    if len(digits) == 11:
        return f'{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}'
    return cpf


def _validate_cpf(cpf: str) -> bool:
    """Valida CPF (dígitos verificadores)."""
    digits = ''.join(filter(str.isdigit, cpf))
    if len(digits) != 11 or digits == digits[0] * 11:
        return False
    # Primeiro dígito
    total = sum(int(digits[i]) * (10 - i) for i in range(9))
    r = (total * 10 % 11) % 10
    if r != int(digits[9]):
        return False
    # Segundo dígito
    total = sum(int(digits[i]) * (11 - i) for i in range(10))
    r = (total * 10 % 11) % 10
    return r == int(digits[10])


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
    # Bypass de autenticação para desenvolvimento
    if os.environ.get('BYPASS_AUTH') == '1':
        session['user'] = {
            'username': 'dev_user',
            'display_name': 'Dev User',
            'email': 'dev@dev.local',
        }
        session['is_admin'] = False
        return redirect(url_for('video.home'))

    # Se já estiver logado, redirecionar para home
    if 'user' in session:
        return redirect(url_for('video.home'))

    if request.method == 'POST':
        cpf_input = request.form.get('cpf', '').strip()
        password = request.form.get('password', '')

        if not cpf_input or not password:
            flash('Por favor, preencha o CPF e a senha.', 'error')
            return render_template('login.html')

        if not _validate_cpf(cpf_input):
            flash('CPF inválido.', 'error')
            return render_template('login.html')

        user = get_user_by_cpf(cpf_input)

        if not user or not user.get('password_hash'):
            flash('CPF não encontrado. Faça seu cadastro primeiro.', 'error')
            return render_template('login.html')

        if not check_password_hash(user['password_hash'], password):
            flash('CPF ou senha inválidos.', 'error')
            return render_template('login.html')

        # Autenticação bem-sucedida
        session.permanent = True
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        session['user'] = {
            'username': user['username'],
            'display_name': user.get('display_name') or user['username'],
            'email': user['email'],
        }
        session['is_admin'] = bool(user.get('is_admin', False))

        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        register_session(session['session_id'], user['username'], ip_address, user_agent)

        flash(f'Bem-vindo, {session["user"]["display_name"]}!', 'success')

        if session['is_admin']:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('video.home'))

    return render_template('login.html')


# ---------------------------------------------------------------------------
# Cadastro
# ---------------------------------------------------------------------------

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rota de cadastro"""
    if 'user' in session:
        return redirect(url_for('video.home'))

    if request.method == 'POST':
        display_name = request.form.get('display_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        cpf_input = request.form.get('cpf', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validações básicas
        if not all([display_name, email, cpf_input, password, password_confirm]):
            flash('Preencha todos os campos.', 'error')
            return render_template('register.html')

        if not _email_allowed(email):
            flash(f'Apenas e-mails {ALLOWED_DOMAIN} são permitidos para cadastro.', 'error')
            return render_template('register.html')

        if not re.fullmatch(r'[^@\s]+@pedragon\.com\.br', email):
            flash('Formato de e-mail inválido.', 'error')
            return render_template('register.html')

        if not _validate_cpf(cpf_input):
            flash('CPF inválido. Verifique os dígitos informados.', 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('A senha deve ter no mínimo 8 caracteres.', 'error')
            return render_template('register.html')

        if password != password_confirm:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html')

        # Verificar se CPF já cadastrado
        if get_user_by_cpf(cpf_input):
            flash('Este CPF já está cadastrado. Faça login.', 'error')
            return render_template('register.html')

        # Verificar se e-mail já cadastrado
        if get_user_by_email(email):
            flash('Este e-mail já está cadastrado.', 'error')
            return render_template('register.html')

        username = _email_to_username(email)

        # Verificar se username já existe (pode haver colisão)
        if get_user(username):
            flash('Nome de usuário derivado do e-mail já está em uso. Entre em contato com o suporte.', 'error')
            return render_template('register.html')

        cpf_formatted = _format_cpf(cpf_input)
        password_hash = generate_password_hash(password)
        create_local_user(username, email, display_name, password_hash, cpf_formatted)

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@auth_bp.route('/logout')
def logout():
    """Rota de logout"""
    if 'session_id' in session:
        remove_session(session['session_id'])

    session.pop('user', None)
    session.pop('is_admin', None)
    session.pop('session_id', None)
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

