"""
Rotas relacionadas ao usuário (perfil, cursos)
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from .middleware import login_required, get_current_user, get_current_username
from .database import get_user, create_or_update_user, get_user_progress, get_exam_results, update_profile_picture
from .video_routes import format_video_name
from .config import VIDEOS_DIR, VIDEO_EXTENSIONS, WATCHED_THRESHOLD
import os

AVATAR_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
AVATAR_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'avatars')

# Criação do blueprint
user_bp = Blueprint('user', __name__)


@user_bp.route('/my-courses')
@login_required
def my_courses():
    """Rota para exibir os cursos selecionados pelo usuário no perfil"""
    import json
    username = get_current_username()
    
    if not username:
        return redirect(url_for('auth.login'))
    
    # Obter cursos selecionados pelo usuário
    user_db = get_user(username)
    selected_courses = []
    if user_db and user_db.get('selected_courses'):
        selected_courses_json = user_db.get('selected_courses')
        try:
            selected_courses = json.loads(selected_courses_json) if isinstance(selected_courses_json, str) else selected_courses_json
        except:
            selected_courses = []
    
    # Carregar progresso do usuário do banco de dados
    user_progress = get_user_progress(username)
    
    # Organizar cursos selecionados com seus status
    # Agrupar cursos por módulo (categoria = parte antes da '/')
    modules = {}

    for topic_name in selected_courses:
        # Separar categoria e nome do curso
        if '/' in topic_name:
            category_name, course_name = topic_name.split('/', 1)
        else:
            category_name, course_name = topic_name, topic_name

        topic_progress = user_progress.get(topic_name, {})

        # Contar vídeos do tópico
        topic_path = os.path.join(VIDEOS_DIR, topic_name)
        total_videos = 0
        if os.path.exists(topic_path) and os.path.isdir(topic_path):
            videos = [f for f in os.listdir(topic_path) if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS]
            total_videos = len(videos)

        # Calcular progresso
        videos_completed = 0
        videos_in_progress = 0
        for video_name, progress in topic_progress.items():
            current_time = progress.get('current_time', 0)
            duration = progress.get('duration', 0)
            if duration > 0:
                pct = (current_time / duration) * 100
                if pct >= 90:
                    videos_completed += 1
                elif current_time > 0:
                    videos_in_progress += 1

        if videos_completed == total_videos and total_videos > 0:
            status = 'concluído'
        elif videos_completed > 0 or videos_in_progress > 0:
            status = 'em andamento'
        else:
            status = 'não iniciado'

        completion_percent = (videos_completed / total_videos * 100) if total_videos > 0 else 0

        course_entry = {
            'topic': topic_name,
            'course_name': course_name,
            'status': status,
            'completion_percent': completion_percent,
            'total_videos': total_videos,
            'videos_completed': videos_completed,
            'videos_in_progress': videos_in_progress,
        }

        if category_name not in modules:
            modules[category_name] = {
                'category_name': category_name,
                'courses': [],
                'total_videos': 0,
                'videos_completed': 0,
            }

        modules[category_name]['courses'].append(course_entry)
        modules[category_name]['total_videos'] += total_videos
        modules[category_name]['videos_completed'] += videos_completed

    # Calcular progresso geral do módulo
    for mod in modules.values():
        tv = mod['total_videos']
        mod['avg_completion'] = round(mod['videos_completed'] / tv * 100) if tv > 0 else 0

    modules = dict(sorted(modules.items(), key=lambda x: x[0].lower()))

    return render_template('my_courses.html', modules=modules, user=username)


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
    
    # Contar total de vídeos disponíveis (estrutura: /videos/categoria/curso/video.mp4)
    total_videos = 0
    all_topics = {}  # {"categoria/curso": [videos]}

    if os.path.exists(VIDEOS_DIR):
        for category in sorted(os.listdir(VIDEOS_DIR)):
            category_path = os.path.join(VIDEOS_DIR, category)
            if not os.path.isdir(category_path):
                continue
            for course in sorted(os.listdir(category_path)):
                course_path = os.path.join(category_path, course)
                if not os.path.isdir(course_path):
                    continue
                videos = [f for f in os.listdir(course_path)
                         if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS]
                if videos:
                    topic_key = f"{category}/{course}"
                    all_topics[topic_key] = videos
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

    # Calcular progresso baseado APENAS nos cursos selecionados
    selected_total = 0
    selected_watched = 0
    for topic_name in selected_courses:
        topic_videos = all_topics.get(topic_name, [])
        selected_total += len(topic_videos)
        topic_progress = user_progress.get(topic_name, {})
        for video_file in topic_videos:
            prog = topic_progress.get(video_file, {})
            ct = prog.get('current_time', 0)
            dur = prog.get('duration', 0)
            if dur > 0 and (ct / dur) >= WATCHED_THRESHOLD:
                selected_watched += 1
    selected_completion = round(selected_watched / selected_total * 100, 1) if selected_total > 0 else 0

    stats = {
        'total_videos': total_videos,
        'videos_watched': videos_watched,
        'videos_in_progress': videos_in_progress,
        'videos_pending': videos_pending,
        'completion_percent': round(completion_percent, 1),
        'total_watch_time': f"{total_hours}h {total_minutes}min" if total_hours > 0 else f"{total_minutes}min",
        'total_topics': len(all_topics),
        'selected_total': selected_total,
        'selected_watched': selected_watched,
        'selected_completion': selected_completion,
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
    
    # Preparar lista de tópicos agrupados por categoria para o modal
    available_by_category = {}
    for topic_key in sorted(all_topics.keys()):
        cat = topic_key.split('/', 1)[0] if '/' in topic_key else topic_key
        available_by_category.setdefault(cat, []).append(topic_key)

    available_topics = sorted(all_topics.keys())
    
    print(f"\n{'='*80}")
    print(f"DEBUG PROFILE - Usuário: {username}")
    print(f"DEBUG PROFILE - Total de tópicos disponíveis: {len(available_topics)}")
    print(f"DEBUG PROFILE - Tópicos: {available_topics}")
    print(f"DEBUG PROFILE - Cursos selecionados: {selected_courses}")
    print(f"{'='*80}\n")
    
    return render_template('profile.html', user=user_data, stats=stats, additional_data=additional_data,
                         exam_scores=exam_scores, available_topics=available_topics,
                         available_by_category=available_by_category,
                         selected_courses=selected_courses,
                         profile_picture=user_db.get('profile_picture') if user_db else None)


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
        
        # Atualizar dados no banco com preserve_existing=True
        # para não sobrescrever campos que não foram alterados
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
            selected_courses=selected_courses if selected_courses else None,
            preserve_existing=True
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


@user_bp.route('/profile/remove-course', methods=['POST'])
@login_required
def remove_course():
    """Remove um curso da lista de cursos selecionados do usuário"""
    import json
    username = get_current_username()
    if not username:
        flash('Usuário não autenticado.', 'error')
        return redirect(url_for('auth.login'))

    course_to_remove = request.form.get('course', '').strip()
    redirect_to = request.form.get('redirect_to', 'profile')

    if not course_to_remove:
        flash('Curso não especificado.', 'error')
        return redirect(url_for('user.profile'))

    user_db = get_user(username)
    selected_courses = []
    if user_db and user_db.get('selected_courses'):
        try:
            sc = user_db.get('selected_courses')
            selected_courses = json.loads(sc) if isinstance(sc, str) else sc
        except Exception:
            selected_courses = []

    if course_to_remove in selected_courses:
        selected_courses.remove(course_to_remove)
        create_or_update_user(
            username=username,
            selected_courses=selected_courses,
            preserve_existing=True
        )
        flash('Curso removido dos seus cursos de interesse.', 'success')
    else:
        flash('Curso não encontrado na sua lista.', 'error')

    if redirect_to == 'my_courses':
        return redirect(url_for('user.my_courses'))
    return redirect(url_for('user.profile'))


@user_bp.route('/profile/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Rota para upload de foto de perfil"""
    username = get_current_username()
    if not username:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    file = request.files.get('avatar')
    if not file or file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('user.profile'))

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in AVATAR_EXTENSIONS:
        flash('Formato inválido. Use JPG, PNG, GIF ou WEBP.', 'error')
        return redirect(url_for('user.profile'))

    # Limita tamanho a 5MB
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > 5 * 1024 * 1024:
        flash('A imagem deve ter no máximo 5MB.', 'error')
        return redirect(url_for('user.profile'))

    os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

    # Remove avatar anterior se existir
    for old_ext in AVATAR_EXTENSIONS:
        old_path = os.path.join(AVATAR_UPLOAD_DIR, f"{username}{old_ext}")
        if os.path.exists(old_path):
            os.remove(old_path)

    filename = f"{username}{ext}"
    filepath = os.path.join(AVATAR_UPLOAD_DIR, filename)
    file.save(filepath)

    update_profile_picture(username, filename)

    flash('Foto de perfil atualizada com sucesso!', 'success')
    return redirect(url_for('user.profile'))
