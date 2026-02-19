# -*- coding: utf-8 -*-
"""
Rotas para gerenciamento e visualização de vídeos
"""
from flask import Blueprint, render_template, send_from_directory, flash, redirect, url_for
from .middleware import login_required, profile_complete_required, get_current_user
from .config import VIDEOS_DIR, VIDEO_EXTENSIONS
import os
import sys
import mimetypes
import re

# Criação do blueprint
video_bp = Blueprint('video', __name__)


# Dicionário de correções para palavras sem acentuação
PALAVRA_CORRECOES = {
    'reimpressao': 'Reimpressão',
    'requisicao': 'Requisição',
    'manutencao': 'Manutenção',
    'marcacao': 'Marcação',
    'avaliacao': 'Avaliação',
    'atencao': 'Atenção',
    'analise': 'Análise',
    'situacao': 'Situação',
    'relatorio': 'Relatório',
    'relatorios': 'Relatórios',
    'veiculos': 'Veículos',
    'veiculo': 'Veículo',
    'usuario': 'Usuário',
    'usuarios': 'Usuários',
    'historico': 'Histórico',
    'garantia': 'Garantia',
    'lancamento': 'Lançamento',
    'basico': 'Básico',
    'basica': 'Básica',
    'servico': 'Serviço',
    'servicos': 'Serviços',
    'orcamento': 'Orçamento',
    'credito': 'Crédito',
    'debito': 'Débito',
    'funcionario': 'Funcionário',
    'funcionarios': 'Funcionários',
    'operacao': 'Operação',
    'operacoes': 'Operações',
    'periodo': 'Período',
    'pedido': 'Pedido',
    'pedidos': 'Pedidos',
    'importacao': 'Importação',
    'exportacao': 'Exportação',
    'comissao': 'Comissão',
    'comissoes': 'Comissões',
    'area': 'Área',
    'areas': 'Áreas',
    'codigo': 'Código',
    'codigos': 'Códigos',
    'numero': 'Número',
    'numeros': 'Números',
    'parametro': 'Parâmetro',
    'parametros': 'Parâmetros',
    'secao': 'Seção',
    'secoes': 'Seções',
    'transacao': 'Transação',
    'transacoes': 'Transações',
    'validacao': 'Validação',
    'validacoes': 'Validações',
    'tecnico': 'Técnico',
    'tecnica': 'Técnica',
    'tecnicos': 'Técnicos',
    'tecnicas': 'Técnicas',
    'conferencia': 'Conferência',
    'vinculo': 'Vínculo',
    'vinculos': 'Vínculos',
    'implantacao': 'Implantação',
    'geracao': 'Geração',
    'configuracao': 'Configuração',
    'configuracoes': 'Configurações',
    'conciliacao': 'Conciliação',
    'integracao': 'Integração',
    'integracoes': 'Integrações',
    'devolucao': 'Devolução',
    'devolucoes': 'Devoluções',
    'consulta': 'Consulta',
    'consultas': 'Consultas',
    'familia': 'Família',
    'familias': 'Famílias',
    'estoque': 'Estoque',
    'estoques': 'Estoques',
    'balanco': 'Balanço',
    'balancos': 'Balanços',
    'movimentacao': 'Movimentação',
    'movimentacoes': 'Movimentações',
    'provisao': 'Provisão',
    'provisoes': 'Provisões',
    'titulo': 'Título',
    'titulos': 'Títulos',
    'nota': 'Nota',
    'notas': 'Notas',
    'fatura': 'Fatura',
    'faturas': 'Faturas',
    'contas': 'Contas',
    'conta': 'Conta',
    'eletronico': 'Eletrônico',
    'eletronica': 'Eletrônica',
    'eletronicos': 'Eletrônicos',
    'eletronicas': 'Eletrônicas',
    'nfe': 'NF-e',
    'oficina': 'Oficina',
    'oficinas': 'Oficinas',
    'mecanico': 'Mecânico',
    'mecanica': 'Mecânica',
    'mecanicos': 'Mecânicos',
    'mecanicas': 'Mecânicas',
    'auditoria': 'Auditoria',
    'auditorias': 'Auditorias',
    'categoria': 'Categoria',
    'categorias': 'Categorias',
    'financeiro': 'Financeiro',
    'financeira': 'Financeira',
    'financeiros': 'Financeiros',
    'financeiras': 'Financeiras',
    'contabil': 'Contábil',
    'contabeis': 'Contábeis',
    'fiscal': 'Fiscal',
    'fiscais': 'Fiscais',
    'pecas': 'Peças',
    'peca': 'Peça',
    'endereco': 'Endereço',
    'enderecos': 'Endereços',
    'secretaria': 'Secretaria',
    'secretarias': 'Secretarias',
    'secretario': 'Secretário',
    'secretarios': 'Secretários',
    'balcao': 'Balcão',
    'balcoes': 'Balcões',
    'garantista': 'Garantista',
    'garantistas': 'Garantistas',
    'recepcao': 'Recepção',
    'satisfacao': 'Satisfação',
    'agendamento': 'Agendamento',
    'agendamentos': 'Agendamentos',
    'auditoria': 'Auditoria',
    'boqueta': 'Boqueta',
    'contabil': 'Contábil',
    'gerencia': 'Gerência',
    'gerencias': 'Gerências',
    'producao': 'Produção',
    'producoes': 'Produções',
    'promocao': 'Promoção',
    'promocoes': 'Promoções',
}


def format_video_name(filename):
    """
    Formata o nome do arquivo de vídeo para exibição
    Remove prefixo numérico, underscores e extensão
    Corrige palavras sem acentuação
    Exemplo: 01_Dealernet_Workflow_-_Login_do_Sistema.mp4 
    -> Dealernet Workflow - Login do Sistema
    """
    # Remove a extensão
    name = os.path.splitext(filename)[0]
    
    # Remove prefixo numérico (ex: 01_, 02_, etc)
    name = re.sub(r'^\d+_', '', name)
    
    # Substitui underscores por espaços
    name = name.replace('_', ' ')
    
    # Divide em palavras
    words = name.split()
    formatted_words = []
    small_words = ['de', 'do', 'da', 'dos', 'das', 'e', 'a', 'o', 'em', 'para', 'com', 'sem', 'por', 'ao', 'aos']
    
    for i, word in enumerate(words):
        word_lower = word.lower()
        
        # Verifica se a palavra precisa de correção de acentuação
        if word_lower in PALAVRA_CORRECOES:
            # Se for a primeira palavra, mantém maiúscula
            if i == 0:
                formatted_words.append(PALAVRA_CORRECOES[word_lower])
            else:
                # Para outras posições, usa a versão do dicionário mas pode ajustar caso
                corrected = PALAVRA_CORRECOES[word_lower]
                formatted_words.append(corrected)
        # Primeira palavra sempre maiúscula
        elif i == 0 or word_lower not in small_words:
            formatted_words.append(word.capitalize())
        else:
            formatted_words.append(word_lower)
    
    return ' '.join(formatted_words)


def get_all_topics():
    """Retorna todos os tópicos e seus vídeos.
    
    Estrutura de diretórios esperada:
        VIDEOS_DIR/topico/pasta_do_curso/video.mp4
    
    Retorna um dicionário cujas chaves são 'topico/pasta_do_curso'.
    """
    topics = {}
    
    try:
        if os.path.exists(VIDEOS_DIR):
            # Nível 1: categorias/tópicos gerais
            for category_name in os.listdir(VIDEOS_DIR):
                category_path = os.path.join(VIDEOS_DIR, category_name)
                
                if not os.path.isdir(category_path):
                    continue
                
                # Nível 2: pastas dos cursos dentro de cada categoria
                for course_name in os.listdir(category_path):
                    course_path = os.path.join(category_path, course_name)
                    
                    if not os.path.isdir(course_path):
                        continue
                    
                    # Nível 3: arquivos de vídeo dentro do curso
                    video_files = []
                    for file_name in os.listdir(course_path):
                        file_path = os.path.join(course_path, file_name)
                        if os.path.isfile(file_path):
                            ext = os.path.splitext(file_name)[1].lower()
                            if ext in VIDEO_EXTENSIONS:
                                video_files.append(file_name)
                    
                    if video_files:
                        # Chave composta: 'topico/pasta_do_curso'
                        topic_key = f"{category_name}/{course_name}"
                        topics[topic_key] = sorted(video_files)
        
        # Ordenar os tópicos alfabeticamente pela chave composta
        topics = dict(sorted(topics.items(), key=lambda x: x[0].lower()))
        
        print(f"Debug - Tópicos encontrados: {list(topics.keys())}")
        print(f"Debug - Total de tópicos: {len(topics)}")
        
    except Exception as e:
        print(f"Erro ao ler diretório de vídeos: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return topics


@video_bp.route('/home')
@login_required
@profile_complete_required
def home():
    """Página inicial com Hero Section — vídeos mais assistidos baseados em dados reais"""
    from .database import get_video_view_counts
    import os

    user = get_current_user()

    # Busca vídeos mais assistidos do banco
    video_rows = get_video_view_counts()

    popular_videos = []
    for row in video_rows[:6]:
        topic_name = row['topic']
        video_name = row['video_name']
        views = int(row['views'])
        unique_users = int(row['unique_users'])

        # Nome do curso (parte após a primeira '/')
        course_display = topic_name.split('/', 1)[1] if '/' in topic_name else topic_name
        # Nome do vídeo sem extensão
        video_display = os.path.splitext(video_name)[0]

        popular_videos.append({
            'topic_name': topic_name,
            'course_display': course_display,
            'video_name': video_name,
            'views': views,
            'unique_users': unique_users,
        })

    return render_template('home.html', user=user, popular_videos=popular_videos)


@video_bp.route('/all-courses')
@login_required
@profile_complete_required
def all_courses():
    """Página com todos os módulos/categorias disponíveis"""
    from .progress_routes import calculate_topic_completion
    from .middleware import get_current_username
    from .database import get_user
    import json

    user = get_current_user()
    username = get_current_username()

    # Obter cursos já adicionados pelo usuário
    user_db = get_user(username)
    selected_courses = []
    if user_db and user_db.get('selected_courses'):
        selected_courses_json = user_db.get('selected_courses')
        try:
            selected_courses = json.loads(selected_courses_json) if isinstance(selected_courses_json, str) else selected_courses_json
        except:
            selected_courses = []

    # Obter TODOS os tópicos disponíveis
    all_topics = get_all_topics()

    # Agrupar por categoria (primeiro nível do path)
    # topic_name = "Categoria/NomeCurso"
    categories = {}
    for topic_key, videos in all_topics.items():
        category_name, course_name = topic_key.split('/', 1)
        completion = calculate_topic_completion(username, topic_key, len(videos))

        if category_name not in categories:
            categories[category_name] = {
                'courses': [],
                'total_videos': 0,
                'added_count': 0,
                'total_completion': 0,
            }

        categories[category_name]['courses'].append({
            'topic_key': topic_key,
            'course_name': course_name,
            'video_count': len(videos),
            'completion': completion,
            'is_added': topic_key in selected_courses,
        })
        categories[category_name]['total_videos'] += len(videos)
        categories[category_name]['total_completion'] += completion
        if topic_key in selected_courses:
            categories[category_name]['added_count'] += 1

    # Calcular progresso médio por categoria
    for cat in categories.values():
        n = len(cat['courses'])
        cat['avg_completion'] = round(cat['total_completion'] / n) if n else 0

    categories = dict(sorted(categories.items(), key=lambda x: x[0].lower()))

    return render_template('all_courses.html', user=user, categories=categories)


@video_bp.route('/category/<path:category_name>')
@login_required
@profile_complete_required
def category_detail(category_name):
    """Página de detalhes de uma categoria com seus cursos"""
    from .progress_routes import calculate_topic_completion
    from .middleware import get_current_username
    from .database import get_user
    import json

    user = get_current_user()
    username = get_current_username()

    # Verificar se a categoria existe
    category_path = os.path.join(VIDEOS_DIR, category_name)
    if not os.path.exists(category_path) or not os.path.isdir(category_path):
        flash(f'Módulo "{category_name}" não encontrado.', 'error')
        return redirect(url_for('video.all_courses'))

    # Obter cursos já adicionados pelo usuário
    user_db = get_user(username)
    selected_courses = []
    if user_db and user_db.get('selected_courses'):
        selected_courses_json = user_db.get('selected_courses')
        try:
            selected_courses = json.loads(selected_courses_json) if isinstance(selected_courses_json, str) else selected_courses_json
        except:
            selected_courses = []

    # Obter todos os tópicos e filtrar por categoria
    all_topics = get_all_topics()
    courses = {}
    for topic_key, videos in all_topics.items():
        if topic_key.startswith(category_name + '/'):
            course_name = topic_key.split('/', 1)[1]
            completion = calculate_topic_completion(username, topic_key, len(videos))
            courses[topic_key] = {
                'course_name': course_name,
                'videos': videos,
                'video_count': len(videos),
                'completion': completion,
                'is_added': topic_key in selected_courses,
            }

    courses = dict(sorted(courses.items(), key=lambda x: x[0].lower()))

    return render_template('category_detail.html', user=user,
                           category_name=category_name, courses=courses)


@video_bp.route('/add-course/<path:topic_name>', methods=['POST'])
@login_required
@profile_complete_required
def add_course(topic_name):
    """Adiciona um curso aos cursos selecionados do usuário"""
    from .middleware import get_current_username
    from .database import get_user, create_or_update_user
    import json
    
    username = get_current_username()
    
    if not username:
        flash('Usuário não autenticado.', 'error')
        return redirect(url_for('auth.login'))
    
    # Verificar se o tópico existe
    topic_path = os.path.join(VIDEOS_DIR, topic_name)
    if not os.path.exists(topic_path) or not os.path.isdir(topic_path):
        flash(f'Curso "{topic_name}" não encontrado.', 'error')
        return redirect(url_for('video.all_courses'))
    
    # Obter cursos já selecionados
    user_db = get_user(username)
    selected_courses = []
    if user_db and user_db.get('selected_courses'):
        selected_courses_json = user_db.get('selected_courses')
        try:
            selected_courses = json.loads(selected_courses_json) if isinstance(selected_courses_json, str) else selected_courses_json
        except:
            selected_courses = []
    
    # Adicionar curso se não estiver na lista
    if topic_name not in selected_courses:
        selected_courses.append(topic_name)
        create_or_update_user(
            username=username,
            selected_courses=selected_courses,
            preserve_existing=True
        )
        flash(f'Curso "{topic_name}" adicionado com sucesso!', 'success')
        print(f"✓ Curso '{topic_name}' adicionado aos cursos selecionados de {username}")
    else:
        flash(f'Curso "{topic_name}" já está nos seus cursos.', 'info')
    
    # Redirecionar para a página do curso
    return redirect(url_for('video.topic_detail', topic_name=topic_name))


@video_bp.route('/topic/<path:topic_name>')
@login_required
@profile_complete_required
def topic_detail(topic_name):
    """Página de detalhes de um tópico específico com seus vídeos"""
    from .progress_routes import calculate_topic_completion
    from .middleware import get_current_username
    from .database import get_user_progress
    
    user = get_current_user()
    username = get_current_username()
    topic_path = os.path.join(VIDEOS_DIR, topic_name)
    
    videos = []
    
    try:
        if os.path.exists(topic_path) and os.path.isdir(topic_path):
            # Listar todos os arquivos de vídeo na pasta
            file_names = os.listdir(topic_path)
            
            for file_name in file_names:
                file_path = os.path.join(topic_path, file_name)
                
                # Verificar se é um arquivo e tem extensão de vídeo
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext in VIDEO_EXTENSIONS:
                        videos.append(file_name)
            
            videos = sorted(videos)
            print(f"Debug - Vídeos encontrados em '{topic_name}': {len(videos)}")
        else:
            flash(f'Tópico "{topic_name}" não encontrado.', 'error')
            return redirect(url_for('video.home'))
        
    except Exception as e:
        print(f"Erro ao ler tópico: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Erro ao carregar os vídeos do tópico.', 'error')
        return redirect(url_for('video.home'))
    
    # Obter progresso individual de cada vídeo
    user_progress = get_user_progress(username, topic_name)
    topic_progress = user_progress.get(topic_name, {})
    
    # Criar lista de vídeos com informação de conclusão
    videos_with_status = []
    for video_name in videos:
        video_progress = topic_progress.get(video_name, {})
        duration = video_progress.get('duration', 0)
        current_time = video_progress.get('current_time', 0)
        
        # Verifica se o vídeo está completo (assistiu >= 90%)
        is_completed = False
        if duration > 0:
            percentage = (current_time / duration) * 100
            is_completed = percentage >= 90 or (current_time >= duration - 1)
        
        videos_with_status.append({
            'name': video_name,
            'completed': is_completed
        })
    
    # Verificar se existe arquivo de prova
    exam_exists = os.path.exists(os.path.join(topic_path, 'prova.json'))

    # Verificar se o usuário foi aprovado na prova deste módulo
    exam_aprovado = False
    if exam_exists:
        from .database import get_user_exam_attempts
        tentativas = get_user_exam_attempts(username, topic_name)
        exam_aprovado = any(t.get('score', 0) >= 70 for t in tentativas)

    # Calcular progresso de conclusão
    completion_percentage = calculate_topic_completion(username, topic_name, len(videos))
    
    return render_template('topic_detail.html', user=user, topic_name=topic_name, videos=videos_with_status, 
                         exam_exists=exam_exists, completion=completion_percentage,
                         exam_aprovado=exam_aprovado)


@video_bp.route('/videos/<path:filepath>')
@login_required
@profile_complete_required
def serve_video(filepath):
    """Serve arquivos de vídeo do diretório local com suporte a streaming e Range requests.
    
    O parâmetro 'filepath' é o caminho completo relativo a VIDEOS_DIR, ex:
        topico/pasta_do_curso/video.mp4
    """
    from flask import request, Response
    
    # Separar o nome do arquivo do restante do caminho
    path_parts = filepath.rsplit('/', 1)
    if len(path_parts) != 2:
        return "Caminho inválido", 400
    topic, filename = path_parts

    topic_path = os.path.join(VIDEOS_DIR, topic)
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
        
        # Obter tamanho do arquivo
        file_size = os.path.getsize(file_path)
        
        # Verificar se é uma requisição Range
        range_header = request.headers.get('Range', None)
        
        if not range_header:
            # Requisição normal - enviar arquivo completo
            print(f"Servindo vídeo completo: {filename} ({file_size} bytes)")
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            response = Response(
                data,
                206 if range_header else 200,
                mimetype=mime_type,
                direct_passthrough=False
            )
            response.headers['Content-Length'] = file_size
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Cache-Control'] = 'public, max-age=3600'
            
            return response
        
        # Processar Range request
        # Range header format: "bytes=start-end"
        byte_start = 0
        byte_end = file_size - 1
        
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            groups = match.groups()
            
            if groups[0]:
                byte_start = int(groups[0])
            if groups[1]:
                byte_end = int(groups[1])
        
        # Garantir que os valores estão dentro do range válido
        byte_start = max(0, byte_start)
        byte_end = min(byte_end, file_size - 1)
        length = byte_end - byte_start + 1
        
        print(f"Range request: {filename} - bytes {byte_start}-{byte_end}/{file_size}")
        
        # Ler apenas o chunk requisitado
        with open(file_path, 'rb') as f:
            f.seek(byte_start)
            data = f.read(length)
        
        # Criar resposta com status 206 Partial Content
        response = Response(
            data,
            206,
            mimetype=mime_type,
            direct_passthrough=False
        )
        
        # Headers necessários para Range requests
        response.headers['Content-Range'] = f'bytes {byte_start}-{byte_end}/{file_size}'
        response.headers['Content-Length'] = length
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Cache-Control'] = 'public, max-age=3600'
        
        return response
        
    except Exception as e:
        print(f"Erro ao servir vídeo: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Erro ao carregar vídeo: {str(e)}", 500
