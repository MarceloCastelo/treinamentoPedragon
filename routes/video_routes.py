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
    """Retorna todos os tópicos e seus vídeos"""
    topics = {}
    
    try:
        if os.path.exists(VIDEOS_DIR):
            # Listar todas as pastas (tópicos) - os.listdir retorna strings Unicode no Python 3
            topic_names = os.listdir(VIDEOS_DIR)
            
            for topic_name in topic_names:
                topic_path = os.path.join(VIDEOS_DIR, topic_name)
                
                # Verificar se é um diretório
                if os.path.isdir(topic_path):
                    # Listar todos os arquivos de vídeo na pasta
                    video_files = []
                    file_names = os.listdir(topic_path)
                    
                    for file_name in file_names:
                        file_path = os.path.join(topic_path, file_name)
                        
                        # Verificar se é um arquivo e tem extensão de vídeo
                        if os.path.isfile(file_path):
                            ext = os.path.splitext(file_name)[1].lower()
                            if ext in VIDEO_EXTENSIONS:
                                video_files.append(file_name)
                    
                    # Adicionar à estrutura se houver vídeos
                    if video_files:
                        topics[topic_name] = sorted(video_files)
        
        # Ordenar os tópicos alfabeticamente
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
    """Nova página inicial com Hero Section e cards informativos - otimizada"""
    user = get_current_user()
    
    # Buscar apenas os primeiros 6 tópicos para cursos populares
    # Otimização: não processar todos os tópicos, apenas o necessário
    all_topics = get_all_topics()
    
    # Limitar a 6 cursos para melhor performance
    popular_courses = []
    for idx, (topic_name, videos) in enumerate(list(all_topics.items())[:6]):
        popular_courses.append({
            'topic_name': topic_name,
            'video_count': len(videos),
            'views': (6 - idx) * 150  # Simulado: views decrescentes
        })
    
    return render_template('home.html', user=user, popular_courses=popular_courses)


@video_bp.route('/all-courses')
@login_required
@profile_complete_required
def all_courses():
    """Página com todos os cursos disponíveis (antiga home)"""
    from .progress_routes import calculate_topic_completion
    from .middleware import get_current_username
    from .database import get_user
    import json
    
    user = get_current_user()
    username = get_current_username()
    
    # Obter cursos selecionados pelo usuário
    user_db = get_user(username)
    selected_courses = []
    if user_db and user_db.get('selected_courses'):
        selected_courses_json = user_db.get('selected_courses')
        try:
            selected_courses = json.loads(selected_courses_json) if isinstance(selected_courses_json, str) else selected_courses_json
        except:
            selected_courses = []
    
    # Obter todos os tópicos disponíveis
    all_topics = get_all_topics()
    
    # Filtrar apenas os cursos selecionados pelo usuário
    topics = {}
    if selected_courses:
        for topic_name in selected_courses:
            if topic_name in all_topics:
                topics[topic_name] = all_topics[topic_name]
    else:
        # Se não houver cursos selecionados, mostrar todos (comportamento padrão)
        topics = all_topics
    
    print(f"\n{'='*80}")
    print(f"DEBUG ALL-COURSES - Usuário: {username}")
    print(f"DEBUG ALL-COURSES - Cursos selecionados: {selected_courses}")
    print(f"DEBUG ALL-COURSES - Tópicos filtrados: {list(topics.keys())}")
    print(f"{'='*80}\n")
    
    # Calcular progresso de conclusão para cada tópico
    topics_with_progress = {}
    for topic_name, videos in topics.items():
        completion_percentage = calculate_topic_completion(username, topic_name, len(videos))
        topics_with_progress[topic_name] = {
            'videos': videos,
            'completion': completion_percentage
        }
        print(f"DEBUG ALL-COURSES - Tópico '{topic_name}': {len(videos)} vídeos, {completion_percentage}% concluído")
    
    if not topics:
        flash('Nenhum curso selecionado. Acesse seu perfil para selecionar os cursos que deseja fazer.', 'info')
    
    print(f"\nDEBUG ALL-COURSES - Estrutura final: {list(topics_with_progress.keys())}")
    for topic, data in topics_with_progress.items():
        print(f"  - {topic}: {data['completion']}% ({len(data['videos'])} vídeos)")
    print(f"{'='*80}\n")
    
    return render_template('all_courses.html', user=user, topics=topics_with_progress, selected_courses=selected_courses)


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
    
    # Calcular progresso de conclusão
    completion_percentage = calculate_topic_completion(username, topic_name, len(videos))
    
    return render_template('topic_detail.html', user=user, topic_name=topic_name, videos=videos_with_status, 
                         exam_exists=exam_exists, completion=completion_percentage)


@video_bp.route('/videos/<path:topic>/<path:filename>')
@login_required
@profile_complete_required
def serve_video(topic, filename):
    """Serve arquivos de vídeo do diretório local com suporte a streaming e Range requests"""
    from flask import request, Response
    
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
