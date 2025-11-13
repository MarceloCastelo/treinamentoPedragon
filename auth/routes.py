from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory, Response, jsonify
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, SIMPLE
import os
from functools import wraps
from pathlib import Path
import mimetypes
import re
import json
from datetime import datetime

# Criação do blueprint
auth_bp = Blueprint('auth', __name__)

def format_video_name(filename):
    """
    Formata o nome do arquivo de vídeo para exibição
    Remove prefixo numérico, underscores e extensão
    Exemplo: 01_Dealernet_Workflow_-_Login_do_Sistema.mp4 
    -> Dealernet Workflow - Login do Sistema
    """
    # Remove a extensão
    name = os.path.splitext(filename)[0]
    
    # Remove prefixo numérico (ex: 01_, 02_, etc)
    name = re.sub(r'^\d+_', '', name)
    
    # Substitui underscores por espaços
    name = name.replace('_', ' ')
    
    # Capitaliza primeira letra de cada palavra (exceto preposições)
    words = name.split()
    formatted_words = []
    small_words = ['de', 'do', 'da', 'dos', 'das', 'e', 'a', 'o', 'em', 'para']
    
    for i, word in enumerate(words):
        # Primeira palavra sempre maiúscula
        if i == 0 or word.lower() not in small_words:
            formatted_words.append(word.capitalize())
        else:
            formatted_words.append(word.lower())
    
    return ' '.join(formatted_words)

def login_required(f):
    """Decorator para proteger rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def authenticate_ldap(username, password):
    """
    Autentica usuário no Active Directory usando LDAP
    Retorna os dados do usuário se a autenticação for bem-sucedida, None caso contrário
    """
    try:
        # Configurações do LDAP do arquivo .env
        ldap_server = os.environ.get('LDAP_SERVER')
        ldap_domain = os.environ.get('LDAP_DOMAIN')
        ldap_search_base = os.environ.get('LDAP_SEARCH_BASE')
        
        print(f"Debug - LDAP Server: {ldap_server}")
        print(f"Debug - LDAP Domain: {ldap_domain}")
        print(f"Debug - Search Base: {ldap_search_base}")
        
        if not all([ldap_server, ldap_domain, ldap_search_base]):
            print("Erro: Variáveis de ambiente LDAP não configuradas")
            return None
        
        # Criar servidor LDAP
        print(f"Debug - Tentando conectar ao servidor: {ldap_server}")
        server = Server(ldap_server, get_info=ALL)
        
        # Tentar diferentes formatos de autenticação
        auth_successful = False
        conn = None
        
        # Método 1: UPN (User Principal Name) - username@domain.com
        try:
            user_upn = f"{username}@{ldap_domain}"
            print(f"Debug - Tentativa 1: UPN format: {user_upn}")
            conn = Connection(server, user=user_upn, password=password, auto_bind=False)
            if conn.bind():
                print("Debug - Sucesso com formato UPN!")
                auth_successful = True
        except Exception as e:
            print(f"Debug - Falha UPN: {str(e)}")
        
        # Método 2: DN completo (Distinguished Name)
        if not auth_successful:
            try:
                user_dn = f"cn={username},{ldap_search_base}"
                print(f"Debug - Tentativa 2: DN format: {user_dn}")
                conn = Connection(server, user=user_dn, password=password, auto_bind=False)
                if conn.bind():
                    print("Debug - Sucesso com formato DN!")
                    auth_successful = True
            except Exception as e:
                print(f"Debug - Falha DN: {str(e)}")
        
        # Método 3: sAMAccountName simples
        if not auth_successful:
            try:
                print(f"Debug - Tentativa 3: sAMAccountName: {username}")
                conn = Connection(server, user=username, password=password, auto_bind=False)
                if conn.bind():
                    print("Debug - Sucesso com sAMAccountName!")
                    auth_successful = True
            except Exception as e:
                print(f"Debug - Falha sAMAccountName: {str(e)}")
        
        # Se nenhum método funcionou, retornar None
        if not auth_successful:
            print("Debug - Todas as tentativas de autenticação falharam")
            return None
        
        print("Debug - Autenticação bem-sucedida, procedendo com busca de dados")
        
        # Buscar atributos do usuário
        search_filter = f"(sAMAccountName={username})"
        print(f"Debug - Buscando usuário com filtro: {search_filter}")
        
        search_result = conn.search(
            search_base=ldap_search_base,
            search_filter=search_filter,
            attributes=['displayName', 'sAMAccountName', 'mail']
        )
        
        print(f"Debug - Resultado da busca: {search_result}, Entradas encontradas: {len(conn.entries)}")
        
        if conn.entries:
            entry = conn.entries[0]
            print(f"Debug - Usuário encontrado: {entry}")
            
            user_data = {
                'displayName': str(entry.displayName) if entry.displayName else username,
                'sAMAccountName': str(entry.sAMAccountName) if entry.sAMAccountName else username,
                'mail': str(entry.mail) if entry.mail else ''
            }
            
            conn.unbind()
            return user_data
        else:
            print("Debug - Nenhuma entrada encontrada na pesquisa")
            
        conn.unbind()
        
    except Exception as e:
        print(f"Erro na autenticação LDAP: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None

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
            # Salvar dados do usuário na sessão
            session['user'] = user_data
            flash(f'Bem-vindo, {user_data["displayName"]}!', 'success')
            return redirect(url_for('auth.home'))
        else:
            flash('Usuário ou senha inválidos. Tente novamente.', 'error')
            return render_template('login.html')
    
    # GET request - mostrar formulário de login
    # Se já estiver logado, redirecionar para home
    if 'user' in session:
        return redirect(url_for('auth.home'))
    
    return render_template('login.html')

@auth_bp.route('/home')
@login_required
def home():
    """Página inicial protegida com listagem de vídeos por tópico"""
    user = session.get('user')
    
    # Diretório onde estão os vídeos
    videos_dir = r"C:\Users\adtsa\Documents\Marcelo Castelo\Projetos\youtube_downloader\output"
    
    # Estrutura para armazenar tópicos e vídeos
    topics = {}
    
    try:
        if os.path.exists(videos_dir):
            # Listar todas as pastas (tópicos)
            for topic_name in os.listdir(videos_dir):
                topic_path = os.path.join(videos_dir, topic_name)
                
                # Verificar se é um diretório
                if os.path.isdir(topic_path):
                    # Listar todos os arquivos de vídeo na pasta
                    video_files = []
                    for file_name in os.listdir(topic_path):
                        file_path = os.path.join(topic_path, file_name)
                        
                        # Verificar se é um arquivo e tem extensão de vídeo
                        if os.path.isfile(file_path):
                            ext = os.path.splitext(file_name)[1].lower()
                            if ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv']:
                                video_files.append(file_name)
                    
                    # Adicionar à estrutura se houver vídeos
                    if video_files:
                        topics[topic_name] = sorted(video_files)
        
        print(f"Debug - Tópicos encontrados: {list(topics.keys())}")
        print(f"Debug - Total de tópicos: {len(topics)}")
        
    except Exception as e:
        print(f"Erro ao ler diretório de vídeos: {str(e)}")
        flash('Erro ao carregar os vídeos.', 'error')
    
    return render_template('home.html', user=user, topics=topics)

@auth_bp.route('/topic/<path:topic_name>')
@login_required
def topic_detail(topic_name):
    """Página de detalhes de um tópico específico com seus vídeos"""
    user = session.get('user')
    
    # Diretório onde estão os vídeos
    videos_dir = r"C:\Users\adtsa\Documents\Marcelo Castelo\Projetos\youtube_downloader\output"
    topic_path = os.path.join(videos_dir, topic_name)
    
    videos = []
    
    try:
        if os.path.exists(topic_path) and os.path.isdir(topic_path):
            # Listar todos os arquivos de vídeo na pasta
            for file_name in os.listdir(topic_path):
                file_path = os.path.join(topic_path, file_name)
                
                # Verificar se é um arquivo e tem extensão de vídeo
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv']:
                        videos.append(file_name)
            
            videos = sorted(videos)
            print(f"Debug - Vídeos encontrados em '{topic_name}': {len(videos)}")
        else:
            flash(f'Tópico "{topic_name}" não encontrado.', 'error')
            return redirect(url_for('auth.home'))
        
    except Exception as e:
        print(f"Erro ao ler tópico: {str(e)}")
        flash('Erro ao carregar os vídeos do tópico.', 'error')
        return redirect(url_for('auth.home'))
    
    return render_template('topic_detail.html', user=user, topic_name=topic_name, videos=videos)

@auth_bp.route('/videos/<path:topic>/<path:filename>')
@login_required
def serve_video(topic, filename):
    """Serve arquivos de vídeo do diretório local com suporte a streaming"""
    videos_dir = r"C:\Users\adtsa\Documents\Marcelo Castelo\Projetos\youtube_downloader\output"
    topic_path = os.path.join(videos_dir, topic)
    file_path = os.path.join(topic_path, filename)
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return "Arquivo não encontrado", 404
        
        # Detectar o tipo MIME correto
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            mime_type = 'video/mp4'  # Default para vídeos
        
        print(f"Servindo vídeo: {filename} (MIME: {mime_type})")
        
        # Usar send_from_directory com mimetype explícito
        response = send_from_directory(
            topic_path, 
            filename,
            mimetype=mime_type,
            as_attachment=False,
            conditional=True
        )
        
        # Adicionar headers para melhor compatibilidade com streaming
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Cache-Control'] = 'no-cache'
        
        return response
        
    except Exception as e:
        print(f"Erro ao servir vídeo: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Erro ao carregar vídeo: {str(e)}", 500

@auth_bp.route('/logout')
def logout():
    """Rota de logout"""
    # Limpar sessão
    session.pop('user', None)
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

# Funções auxiliares para progresso de vídeo
def get_progress_file():
    """Retorna o caminho do arquivo de progresso"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'video_progress.json')

def load_progress():
    """Carrega o progresso de todos os usuários"""
    progress_file = get_progress_file()
    try:
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar progresso: {e}")
    return {}

def save_progress(progress_data):
    """Salva o progresso de todos os usuários"""
    progress_file = get_progress_file()
    try:
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar progresso: {e}")
        return False

@auth_bp.route('/my-courses')
@login_required
def my_courses():
    """Rota para exibir os cursos em progresso do usuário"""
    user_data = session.get('user')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    # Extrair o username do dicionário de usuário
    username = user_data.get('username', user_data.get('name', ''))
    
    # Carregar progresso do usuário
    all_progress = load_progress()
    user_progress = all_progress.get(username, {})
    
    # Organizar cursos em progresso
    courses_in_progress = []
    
    for topic, videos in user_progress.items():
        for video_name, progress in videos.items():
            if progress.get('current_time', 0) > 0:
                courses_in_progress.append({
                    'topic': topic,
                    'video_name': video_name,
                    'formatted_name': format_video_name(video_name),
                    'current_time': progress.get('current_time', 0),
                    'duration': progress.get('duration', 0),
                    'progress_percent': (progress.get('current_time', 0) / progress.get('duration', 1)) * 100 if progress.get('duration', 0) > 0 else 0,
                    'last_watched': progress.get('last_watched', '')
                })
    
    # Ordenar por data de última visualização (mais recente primeiro)
    courses_in_progress.sort(key=lambda x: x.get('last_watched', ''), reverse=True)
    
    return render_template('my_courses.html', courses=courses_in_progress, user=username)

@auth_bp.route('/save-progress', methods=['POST'])
@login_required
def save_video_progress():
    """API para salvar o progresso do vídeo"""
    try:
        data = request.get_json()
        user_data = session.get('user')
        
        if not user_data:
            return jsonify({'success': False, 'error': 'Usuário não autenticado'}), 401
        
        # Extrair o username do dicionário de usuário
        username = user_data.get('username', user_data.get('name', ''))
        
        topic = data.get('topic')
        video_name = data.get('video_name')
        current_time = data.get('current_time', 0)
        duration = data.get('duration', 0)
        
        if not topic or not video_name:
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
        
        # Carregar progresso existente
        all_progress = load_progress()
        
        # Inicializar estrutura se necessário
        if username not in all_progress:
            all_progress[username] = {}
        if topic not in all_progress[username]:
            all_progress[username][topic] = {}
        
        # Salvar progresso
        all_progress[username][topic][video_name] = {
            'current_time': current_time,
            'duration': duration,
            'last_watched': datetime.now().isoformat()
        }
        
        # Salvar arquivo
        if save_progress(all_progress):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Erro ao salvar'}), 500
            
    except Exception as e:
        print(f"Erro ao salvar progresso: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/get-progress/<topic>/<video_name>')
@login_required
def get_video_progress(topic, video_name):
    """API para obter o progresso de um vídeo específico"""
    try:
        user_data = session.get('user')
        if not user_data:
            return jsonify({'success': False, 'error': 'Usuário não autenticado'}), 401
        
        # Extrair o username do dicionário de usuário
        username = user_data.get('username', user_data.get('name', ''))
        
        all_progress = load_progress()
        user_progress = all_progress.get(username, {}).get(topic, {}).get(video_name, {})
        
        return jsonify({
            'success': True,
            'current_time': user_progress.get('current_time', 0),
            'duration': user_progress.get('duration', 0)
        })
    except Exception as e:
        print(f"Erro ao obter progresso: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/profile')
@login_required
def profile():
    """Rota para exibir o perfil do usuário com estatísticas"""
    user_data = session.get('user')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    # Extrair o username do dicionário de usuário
    username = user_data.get('username', user_data.get('name', ''))
    
    # Diretório de vídeos
    videos_dir = r"C:\Users\adtsa\Documents\Marcelo Castelo\Projetos\youtube_downloader\output"
    
    # Contar total de vídeos disponíveis
    total_videos = 0
    all_topics = {}
    
    if os.path.exists(videos_dir):
        for topic_name in os.listdir(videos_dir):
            topic_path = os.path.join(videos_dir, topic_name)
            if os.path.isdir(topic_path):
                videos = [f for f in os.listdir(topic_path) if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm'))]
                if videos:
                    all_topics[topic_name] = videos
                    total_videos += len(videos)
    
    # Carregar progresso do usuário
    all_progress = load_progress()
    user_progress = all_progress.get(username, {})
    
    # Calcular estatísticas
    videos_watched = 0
    videos_in_progress = 0
    total_watch_time = 0
    
    for topic, videos in user_progress.items():
        for video_name, progress in videos.items():
            current_time = progress.get('current_time', 0)
            duration = progress.get('duration', 0)
            
            if current_time > 0:
                total_watch_time += current_time
                
                # Considera assistido se passou de 90% do vídeo
                if duration > 0 and (current_time / duration) >= 0.9:
                    videos_watched += 1
                else:
                    videos_in_progress += 1
    
    videos_pending = total_videos - videos_watched
    completion_percent = (videos_watched / total_videos * 100) if total_videos > 0 else 0
    
    # Converter tempo total em horas e minutos
    total_hours = int(total_watch_time // 3600)
    total_minutes = int((total_watch_time % 3600) // 60)
    
    stats = {
        'total_videos': total_videos,
        'videos_watched': videos_watched,
        'videos_in_progress': videos_in_progress,
        'videos_pending': videos_pending,
        'completion_percent': round(completion_percent, 1),
        'total_watch_time': f"{total_hours}h {total_minutes}min" if total_hours > 0 else f"{total_minutes}min",
        'total_topics': len(all_topics)
    }
    
    return render_template('profile.html', user=user_data, stats=stats)