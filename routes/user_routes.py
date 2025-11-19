"""
Rotas relacionadas ao usuário (perfil, cursos)
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from .middleware import login_required, get_current_user, get_current_username
from .database import get_user, create_or_update_user, get_user_progress, get_exam_results
from .video_routes import format_video_name
from .config import VIDEOS_DIR, VIDEO_EXTENSIONS, WATCHED_THRESHOLD
import os

# Criação do blueprint
user_bp = Blueprint('user', __name__)


@user_bp.route('/my-courses')
@login_required
def my_courses():
    """Rota para exibir os cursos em progresso do usuário"""
    username = get_current_username()
    
    if not username:
        return redirect(url_for('auth.login'))
    
    # Carregar progresso do usuário do banco de dados
    user_progress = get_user_progress(username)
    
    # Organizar cursos em progresso (apenas os que não estão completos)
    courses_in_progress = []
    
    for topic, videos in user_progress.items():
        for video_name, progress in videos.items():
            current_time = progress.get('current_time', 0)
            duration = progress.get('duration', 1)
            
            # Só incluir se tiver progresso E não estiver completo (menos de 90%)
            if current_time > 0 and duration > 0:
                progress_percent = (current_time / duration) * 100
                
                # Filtrar apenas vídeos em andamento (não completos)
                if progress_percent < 90:
                    courses_in_progress.append({
                        'topic': topic,
                        'video_name': video_name,
                        'formatted_name': format_video_name(video_name),
                        'current_time': current_time,
                        'duration': duration,
                        'progress_percent': progress_percent,
                        'last_watched': progress.get('last_watched', '')
                    })
    
    # Ordenar por data de última visualização (mais recente primeiro)
    courses_in_progress.sort(key=lambda x: x.get('last_watched', ''), reverse=True)
    
    return render_template('my_courses.html', courses=courses_in_progress, user=username)


@user_bp.route('/profile')
@login_required
def profile():
    """Rota para exibir o perfil do usuário com estatísticas"""
    user_data = get_current_user()
    username = get_current_username()
    
    if not username:
        return redirect(url_for('auth.login'))
    
    # Carregar dados adicionais do usuário do banco
    user_db = get_user(username)
    additional_data = {}
    selected_courses = []
    if user_db:
        additional_data = {
            'empresa': user_db.get('empresa', ''),
            'marca': user_db.get('marca', ''),
            'unidade': user_db.get('unidade', ''),
            'setor': user_db.get('setor', ''),
            'cargo': user_db.get('cargo', '')
        }
        # Carregar cursos selecionados
        selected_courses_json = user_db.get('selected_courses')
        if selected_courses_json:
            import json
            try:
                selected_courses = json.loads(selected_courses_json) if isinstance(selected_courses_json, str) else selected_courses_json
            except:
                selected_courses = []
    
    # Contar total de vídeos disponíveis
    total_videos = 0
    all_topics = {}
    
    if os.path.exists(VIDEOS_DIR):
        for topic_name in os.listdir(VIDEOS_DIR):
            topic_path = os.path.join(VIDEOS_DIR, topic_name)
            if os.path.isdir(topic_path):
                videos = [f for f in os.listdir(topic_path) 
                         if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS]
                if videos:
                    all_topics[topic_name] = videos
                    total_videos += len(videos)
    
    # Carregar progresso do usuário do banco
    user_progress = get_user_progress(username)
    
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
                
                # Considera assistido se passou do threshold configurado
                if duration > 0 and (current_time / duration) >= WATCHED_THRESHOLD:
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
    
    # Carregar notas das provas do banco
    exam_results = get_exam_results(username=username)
    user_exam_results = exam_results.get(username, {})
    
    # Processar notas para exibição
    exam_scores = []
    for topic_name, attempts in user_exam_results.items():
        if attempts:
            # Pega a melhor nota
            best_attempt = max(attempts, key=lambda x: x['score'])
            exam_scores.append({
                'modulo': topic_name,
                'nota': best_attempt['score'],
                'aprovado': best_attempt['score'] >= 70,
                'tentativas': len(attempts)
            })
    
    # Ordenar por nome do módulo
    exam_scores.sort(key=lambda x: x['modulo'])
    
    # Preparar lista de todos os tópicos disponíveis
    available_topics = list(all_topics.keys())
    available_topics.sort()
    
    return render_template('profile.html', user=user_data, stats=stats, additional_data=additional_data, 
                         exam_scores=exam_scores, available_topics=available_topics, 
                         selected_courses=selected_courses)


@user_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Rota para atualizar informações adicionais do perfil"""
    username = get_current_username()
    
    if not username:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    
    try:
        # Obter dados do formulário
        empresa = request.form.get('empresa', '').strip()
        marca = request.form.get('marca', '').strip()
        unidade = request.form.get('unidade', '').strip()
        setor = request.form.get('setor', '').strip()
        cargo = request.form.get('cargo', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Obter cursos selecionados (pode vir como lista ou None)
        selected_courses = request.form.getlist('selected_courses')
        
        # Atualizar dados no banco
        result = create_or_update_user(
            username=username,
            email=email if email else None,
            phone=phone if phone else None,
            department=setor,
            position=cargo,
            empresa=empresa,
            marca=marca,
            unidade=unidade,
            setor=setor,
            cargo=cargo,
            selected_courses=selected_courses if selected_courses else None
        )
        
        if result:
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('Erro ao salvar os dados do perfil.', 'error')
            return redirect(url_for('user.profile'))
            
    except Exception as e:
        print(f"Erro ao atualizar perfil: {e}")
        flash('Erro ao atualizar o perfil. Tente novamente.', 'error')
        return redirect(url_for('user.profile'))
