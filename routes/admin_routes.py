"""
Rotas administrativas para gerenciamento do sistema
"""
from flask import Blueprint, render_template, jsonify, session
from .middleware import admin_required, get_current_username
from .config import VIDEOS_DIR, PROGRESS_FILE, WATCHED_THRESHOLD
import json
import os
from datetime import datetime
from collections import defaultdict

# Criação do blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def load_progress_data():
    """Carrega os dados de progresso dos vídeos"""
    progress_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), PROGRESS_FILE)
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar progresso: {e}")
    return {}


def load_user_data():
    """Carrega os dados adicionais dos usuários"""
    user_data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data.json')
    if os.path.exists(user_data_file):
        try:
            with open(user_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados de usuários: {e}")
    return {}


def load_exam_results():
    """Carrega os resultados das provas"""
    exam_results_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exam_results.json')
    if os.path.exists(exam_results_file):
        try:
            with open(exam_results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar resultados de provas: {e}")
    return {}


def get_available_modules():
    """Retorna lista de módulos disponíveis"""
    modules = []
    try:
        if os.path.exists(VIDEOS_DIR):
            for item in os.listdir(VIDEOS_DIR):
                item_path = os.path.join(VIDEOS_DIR, item)
                if os.path.isdir(item_path):
                    modules.append(item)
    except Exception as e:
        print(f"Erro ao listar módulos: {e}")
    return sorted(modules)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Dashboard administrativo principal com métricas analíticas"""
    progress_data = load_progress_data()
    user_data = load_user_data()
    exam_results = load_exam_results()
    modules = get_available_modules()
    
    # Estatísticas gerais
    total_users = len(set(progress_data.keys()) | set(user_data.keys()))
    total_modules = len(modules)
    
    # Usuários ativos (com algum progresso)
    active_users = len([u for u in progress_data.keys() if progress_data[u]])
    
    # Taxa de engajamento
    engagement_rate = round((active_users / total_users * 100) if total_users > 0 else 0, 1)
    
    # Calcular conclusões por módulo
    module_completions = {}
    module_stats = {}
    total_completions = 0
    
    for module in modules:
        completed = 0
        module_exam_scores = []
        module_exam_attempts = []
        
        for username, user_progress in progress_data.items():
            module_videos = {k: v for k, v in user_progress.items() if k.startswith(f"{module}/")}
            if module_videos:
                # Verificar se todos os vídeos do módulo foram assistidos
                all_watched = all(v.get('watched', False) for v in module_videos.values())
                if all_watched and len(module_videos) > 0:
                    completed += 1
                    total_completions += 1
            
            # Estatísticas de provas do módulo
            user_exams = exam_results.get(username, {})
            for topic, topic_data in user_exams.items():
                if isinstance(topic_data, dict) and topic.startswith(module):
                    if 'melhor_nota' in topic_data:
                        module_exam_scores.append(topic_data['melhor_nota'])
                    if 'tentativas' in topic_data:
                        module_exam_attempts.append(len(topic_data['tentativas']))
        
        module_completions[module] = completed
        
        # Calcular taxa de conclusão e métricas do módulo
        users_started = len([u for u in progress_data.keys() 
                           if any(k.startswith(f"{module}/") for k in progress_data[u].keys())])
        
        module_stats[module] = {
            'name': module,
            'completions': completed,
            'completion_rate': round((completed / users_started * 100) if users_started > 0 else 0, 1),
            'avg_score': round(sum(module_exam_scores) / len(module_exam_scores), 1) if module_exam_scores else 0,
            'avg_attempts': round(sum(module_exam_attempts) / len(module_exam_attempts), 1) if module_exam_attempts else 0
        }
    
    # Taxa de conclusão geral
    completion_rate = round((total_completions / (total_users * total_modules) * 100) 
                          if total_users > 0 and total_modules > 0 else 0, 1)
    
    # Top 5 módulos por conclusões
    top_modules = sorted(module_stats.values(), key=lambda x: x['completions'], reverse=True)[:5]
    
    # Estatísticas de provas
    total_exams_taken = 0
    total_exams_passed = 0
    all_scores = []
    
    for username, user_exams in exam_results.items():
        for topic, topic_data in user_exams.items():
            if isinstance(topic_data, dict) and 'tentativas' in topic_data:
                total_exams_taken += len(topic_data['tentativas'])
                if topic_data.get('aprovado', False):
                    total_exams_passed += 1
                if 'melhor_nota' in topic_data:
                    all_scores.append(topic_data['melhor_nota'])
    
    # Performance média
    avg_exam_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    
    # Distribuição de performance
    high_performers = len([s for s in all_scores if s >= 9.0])
    medium_performers = len([s for s in all_scores if 7.0 <= s < 9.0])
    low_performers = len([s for s in all_scores if s < 7.0])
    
    performance_distribution = {
        '< 7.0': len([s for s in all_scores if s < 7.0]),
        '7.0-7.9': len([s for s in all_scores if 7.0 <= s < 8.0]),
        '8.0-8.9': len([s for s in all_scores if 8.0 <= s < 9.0]),
        '9.0-9.4': len([s for s in all_scores if 9.0 <= s < 9.5]),
        '9.5-10': len([s for s in all_scores if s >= 9.5])
    }
    
    # Calcular horas totais assistidas (estimativa: 10 min por vídeo)
    total_videos_watched = sum(
        sum(1 for v in user_progress.values() if v.get('watched', False))
        for user_progress in progress_data.values()
    )
    total_watch_hours = round(total_videos_watched * 10 / 60, 1)
    
    # Usuários por setor
    sector_users = defaultdict(int)
    for username, data in user_data.items():
        sector = data.get('setor', 'Não informado')
        sector_users[sector] += 1
    
    # Calcular reprovações por setor
    sector_failures = defaultdict(int)
    for username, user_exams in exam_results.items():
        user_info = user_data.get(username, {})
        sector = user_info.get('setor', 'Não informado')
        
        for topic, topic_data in user_exams.items():
            if isinstance(topic_data, dict):
                # Contar se o usuário foi reprovado (não aprovado)
                if not topic_data.get('aprovado', False) and 'tentativas' in topic_data and len(topic_data['tentativas']) > 0:
                    sector_failures[sector] += 1
    
    # Criar lista de gargalos por setor (setores com mais reprovações)
    bottlenecks = []
    for sector, failures in sorted(sector_failures.items(), key=lambda x: x[1], reverse=True):
        if failures > 0:
            total_sector = sector_users.get(sector, 0)
            bottlenecks.append({
                'sector': sector,
                'issue': f'{failures} reprovações de {total_sector} usuários',
                'count': failures
            })
    
    bottlenecks = bottlenecks[:5]  # Top 5 setores com mais reprovações
    
    # Identificar oportunidades
    opportunities = []
    
    # Usuários inativos
    inactive_users = total_users - active_users
    if inactive_users > 0:
        opportunities.append({
            'title': 'Ativar usuários inativos',
            'description': f'{inactive_users} usuários ainda não iniciaram treinamento',
            'impact': f'{inactive_users} usuários'
        })
    
    # Módulos com alta taxa de abandono
    for module, stats_data in module_stats.items():
        users_started = len([u for u in progress_data.keys() 
                           if any(k.startswith(f"{module}/") for k in progress_data[u].keys())])
        if users_started > stats_data['completions'] and users_started > 5:
            abandonment = users_started - stats_data['completions']
            if abandonment > users_started * 0.5:  # Mais de 50% de abandono
                opportunities.append({
                    'title': f'Reduzir abandono em {module}',
                    'description': f'{abandonment} usuários iniciaram mas não concluíram',
                    'impact': f'{abandonment} conclusões'
                })
    
    opportunities = opportunities[:3]  # Top 3 oportunidades
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_modules': total_modules,
        'engagement_rate': engagement_rate,
        'completion_rate': completion_rate,
        'total_completions': total_completions,
        'total_exams_taken': total_exams_taken,
        'total_exams_passed': total_exams_passed,
        'exam_pass_rate': round((total_exams_passed / total_exams_taken * 100) if total_exams_taken > 0 else 0, 1),
        'avg_exam_score': avg_exam_score,
        'total_watch_hours': total_watch_hours,
        'high_performers': high_performers,
        'medium_performers': medium_performers,
        'low_performers': low_performers,
        'performance_distribution': performance_distribution,
        'sector_users': dict(sector_users),
        'top_modules': top_modules,
        'bottlenecks': bottlenecks,
        'opportunities': opportunities,
        'module_completions': module_completions,
        'departments': dict(defaultdict(int, {data.get('unidade', 'Não informado'): 1 
                                             for data in user_data.values()})),
        'companies': dict(defaultdict(int, {data.get('empresa', 'Não informado'): 1 
                                           for data in user_data.values()}))
    }
    
    return render_template('admin_dashboard.html', stats=stats, modules=modules)


@admin_bp.route('/users')
@admin_required
def users():
    """Redirecionar para reports - rota legada"""
    from flask import redirect, url_for
    return redirect(url_for('admin.reports'))


@admin_bp.route('/user/<username>')
@admin_required
def user_detail(username):
    """Detalhes de um usuário específico"""
    progress_data = load_progress_data()
    user_data = load_user_data()
    exam_results = load_exam_results()
    modules = get_available_modules()
    
    user_info = user_data.get(username, {})
    user_progress = progress_data.get(username, {})
    user_exams = exam_results.get(username, {})
    
    # Detalhes de progresso por módulo
    modules_detail = {}
    for module in modules:
        module_videos = {k: v for k, v in user_progress.items() if k.startswith(f"{module}/")}
        videos_list = []
        for video_path, video_data in module_videos.items():
            video_name = os.path.basename(video_path)
            videos_list.append({
                'name': video_name,
                'watched': video_data.get('watched', False),
                'progress': round(video_data.get('progress', 0), 1),
                'last_watched': video_data.get('last_watched', 'Nunca')
            })
        
        if videos_list:
            modules_detail[module] = {
                'videos': sorted(videos_list, key=lambda x: x['name']),
                'total': len(videos_list),
                'watched': sum(1 for v in videos_list if v['watched'])
            }
    
    # Detalhes de provas
    exams_detail = []
    for topic, topic_data in user_exams.items():
        if isinstance(topic_data, dict) and 'tentativas' in topic_data:
            attempts = []
            for attempt in topic_data['tentativas']:
                attempts.append({
                    'score': attempt.get('nota', 0),
                    'date': attempt.get('data', 'Data desconhecida'),
                    'passed': attempt.get('nota', 0) >= 7.0
                })
            
            exams_detail.append({
                'topic': topic,
                'best_score': topic_data.get('melhor_nota', 0),
                'passed': topic_data.get('aprovado', False),
                'attempts': attempts,
                'num_attempts': len(attempts)
            })
    
    user_detail = {
        'username': username,
        'info': user_info,
        'modules': modules_detail,
        'exams': exams_detail
    }
    
    return render_template('admin_user_detail.html', user=user_detail)


@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """API endpoint para estatísticas em tempo real"""
    progress_data = load_progress_data()
    user_data = load_user_data()
    exam_results = load_exam_results()
    
    stats = {
        'total_users': len(set(progress_data.keys()) | set(user_data.keys())),
        'active_users': len([u for u in progress_data.keys() if progress_data[u]]),
        'total_progress_records': sum(len(p) for p in progress_data.values()),
        'total_exam_attempts': sum(
            len(topic_data.get('tentativas', [])) 
            for user_exams in exam_results.values() 
            for topic_data in user_exams.values() 
            if isinstance(topic_data, dict)
        )
    }
    
    return jsonify(stats)


@admin_bp.route('/reports')
@admin_required
def reports():
    """Relatório detalhado por empresa, unidade e marca - Otimizado"""
    from flask import request
    
    progress_data = load_progress_data()
    user_data = load_user_data()
    exam_results = load_exam_results()
    
    # Filtros da query string
    filter_empresa = request.args.get('empresa', '')
    filter_unidade = request.args.get('unidade', '')
    filter_marca = request.args.get('marca', '')
    
    # Estrutura otimizada: empresa -> unidade -> marca -> resumo
    report_summary = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
        'total_users': 0,
        'total_progress': 0,
        'total_exams': 0,
        'total_scores': 0,
        'users_with_exams': 0
    })))
    
    # Lista de empresas, unidades e marcas únicos para filtros
    all_empresas = set()
    all_unidades = set()
    all_marcas = set()
    
    # Combinar dados de todos os usuários - processamento otimizado
    all_usernames = set(user_data.keys())  # Apenas usuários com dados preenchidos
    
    for username in all_usernames:
        user_info = user_data.get(username, {})
        
        # Normalizar dados para evitar duplicações por diferenças sutis
        empresa = user_info.get('empresa', 'Não informado').strip()
        unidade = user_info.get('unidade', 'Não informado').strip()
        marca = user_info.get('marca', 'Não informado').strip()
        
        # Adicionar aos conjuntos de filtros
        all_empresas.add(empresa)
        all_unidades.add(unidade)
        all_marcas.add(marca)
        
        # Aplicar filtros se existirem
        if filter_empresa and empresa != filter_empresa:
            continue
        if filter_unidade and unidade != filter_unidade:
            continue
        if filter_marca and marca != filter_marca:
            continue
        
        # Calcular progresso apenas se necessário
        user_progress = progress_data.get(username, {})
        total_videos = len(user_progress)
        watched_videos = sum(1 for v in user_progress.values() if v.get('watched', False))
        progress_percentage = (watched_videos / total_videos * 100) if total_videos > 0 else 0
        
        # Calcular estatísticas de provas de forma otimizada
        user_exams = exam_results.get(username, {})
        total_score = 0
        total_exams = 0
        
        for topic_data in user_exams.values():
            if isinstance(topic_data, dict) and 'melhor_nota' in topic_data:
                total_score += topic_data['melhor_nota']
                total_exams += 1
        
        # Atualizar resumo
        summary = report_summary[empresa][unidade][marca]
        summary['total_users'] += 1
        summary['total_progress'] += progress_percentage
        summary['total_exams'] += total_exams
        if total_exams > 0:
            summary['total_scores'] += total_score
            summary['users_with_exams'] += 1
    
    # Calcular médias para cada marca
    final_report = {}
    for empresa, unidades in sorted(report_summary.items()):
        final_report[empresa] = {}
        for unidade, marcas in sorted(unidades.items()):
            final_report[empresa][unidade] = {}
            for marca, summary in sorted(marcas.items()):
                final_report[empresa][unidade][marca] = {
                    'total_users': summary['total_users'],
                    'avg_progress': round(summary['total_progress'] / summary['total_users'], 1) if summary['total_users'] > 0 else 0,
                    'total_exams': summary['total_exams'],
                    'avg_score': round(summary['total_scores'] / summary['users_with_exams'], 1) if summary['users_with_exams'] > 0 else 0
                }
    
    return render_template('admin_reports.html', 
                         report_data=final_report,
                         all_empresas=sorted(all_empresas),
                         all_unidades=sorted(all_unidades),
                         all_marcas=sorted(all_marcas),
                         filter_empresa=filter_empresa,
                         filter_unidade=filter_unidade,
                         filter_marca=filter_marca)


@admin_bp.route('/api/users-by-group')
@admin_required
def api_users_by_group():
    """API para buscar usuários de um grupo específico (empresa/unidade/marca)"""
    from flask import request
    
    empresa = request.args.get('empresa', '')
    unidade = request.args.get('unidade', '')
    marca = request.args.get('marca', '')
    
    if not all([empresa, unidade, marca]):
        return jsonify({'error': 'Parâmetros empresa, unidade e marca são obrigatórios'}), 400
    
    progress_data = load_progress_data()
    user_data = load_user_data()
    exam_results = load_exam_results()
    
    users_list = []
    
    for username, user_info in user_data.items():
        if (user_info.get('empresa', '').strip() == empresa and 
            user_info.get('unidade', '').strip() == unidade and 
            user_info.get('marca', '').strip() == marca):
            
            user_progress = progress_data.get(username, {})
            total_videos = len(user_progress)
            watched_videos = sum(1 for v in user_progress.values() if v.get('watched', False))
            progress_percentage = round((watched_videos / total_videos * 100) if total_videos > 0 else 0, 1)
            
            # Estatísticas de provas
            user_exams = exam_results.get(username, {})
            exams_data = []
            total_score = 0
            total_exams = 0
            
            for topic, topic_data in user_exams.items():
                if isinstance(topic_data, dict) and 'melhor_nota' in topic_data:
                    exams_data.append({
                        'topic': topic,
                        'score': topic_data['melhor_nota'],
                        'passed': topic_data.get('aprovado', False)
                    })
                    total_score += topic_data['melhor_nota']
                    total_exams += 1
            
            avg_score = round(total_score / total_exams, 1) if total_exams > 0 else 0
            
            users_list.append({
                'username': username,
                'displayName': user_info.get('displayName', username),
                'cargo': user_info.get('cargo', 'Não informado'),
                'setor': user_info.get('setor', 'Não informado'),
                'progress_percentage': progress_percentage,
                'watched_videos': watched_videos,
                'total_videos': total_videos,
                'exams': exams_data,
                'avg_score': avg_score,
                'total_exams': total_exams
            })
    
    # Ordenar por progresso
    users_list.sort(key=lambda x: x['progress_percentage'], reverse=True)
    
    return jsonify(users_list)
