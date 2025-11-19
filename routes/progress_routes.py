"""
Rotas para gerenciamento de progresso de vídeos
"""
from flask import Blueprint, jsonify, request
from .middleware import login_required, get_current_username
from .database import get_user_progress, save_video_progress as db_save_progress, get_all_progress
from datetime import datetime

# Criação do blueprint
progress_bp = Blueprint('progress', __name__)


def load_progress():
    """Carrega o progresso de todos os usuários do banco de dados"""
    return get_all_progress()


@progress_bp.route('/save-progress', methods=['POST'])
@login_required
def save_video_progress():
    """API para salvar o progresso do vídeo"""
    try:
        data = request.get_json()
        username = get_current_username()
        
        if not username:
            return jsonify({'success': False, 'error': 'Usuário não autenticado'}), 401
        
        topic = data.get('topic')
        video_name = data.get('video_name')
        current_time = data.get('current_time', 0)
        duration = data.get('duration', 0)
        
        if not topic or not video_name:
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
        
        # Salvar no banco de dados
        result = db_save_progress(username, topic, video_name, current_time, duration)
        
        if result is not None:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Erro ao salvar'}), 500
            
    except Exception as e:
        print(f"Erro ao salvar progresso: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@progress_bp.route('/get-progress/<topic>/<video_name>')
@login_required
def get_video_progress(topic, video_name):
    """API para obter o progresso de um vídeo específico"""
    try:
        username = get_current_username()
        
        if not username:
            return jsonify({'success': False, 'error': 'Usuário não autenticado'}), 401
        
        user_progress = get_user_progress(username)
        video_progress = user_progress.get(topic, {}).get(video_name, {})
        
        return jsonify({
            'success': True,
            'current_time': video_progress.get('current_time', 0),
            'duration': video_progress.get('duration', 0)
        })
    except Exception as e:
        print(f"Erro ao obter progresso: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@progress_bp.route('/mark-completed', methods=['POST'])
@login_required
def mark_video_completed():
    """API para marcar um vídeo como concluído ao dar play"""
    try:
        data = request.get_json()
        username = get_current_username()
        
        if not username:
            return jsonify({'success': False, 'error': 'Usuário não autenticado'}), 401
        
        topic = data.get('topic')
        video_name = data.get('video_name')
        duration = data.get('duration', 0)
        
        if not topic or not video_name:
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
        
        # Marcar como concluído (progresso = duração completa) no banco
        result = db_save_progress(username, topic, video_name, duration, duration)
        
        if result is not None:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Erro ao salvar'}), 500
            
    except Exception as e:
        print(f"Erro ao marcar como concluído: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def calculate_topic_completion(username, topic, total_videos):
    """Calcula a porcentagem de conclusão de um tópico"""
    user_progress = get_user_progress(username)
    topic_progress = user_progress.get(topic, {})
    
    print(f"Debug - calculate_topic_completion - Username: {username}, Topic: {topic}, Total Videos: {total_videos}")
    print(f"Debug - user_progress para '{topic}': {topic_progress}")
    
    if not topic_progress or total_videos == 0:
        print(f"Debug - Retornando 0% (sem progresso ou sem vídeos)")
        return 0
    
    completed_videos = 0
    for video_name, progress in topic_progress.items():
        # Considera concluído se assistiu pelo menos 90%
        duration = progress.get('duration', 0)
        current_time = progress.get('current_time', 0)
        
        print(f"Debug - Vídeo '{video_name}': duration={duration}, current_time={current_time}")
        
        if duration > 0:
            percentage = (current_time / duration) * 100
            # Considera concluído se >= 90%, ou se current_time == duration
            if percentage >= 90 or (current_time >= duration - 1):
                completed_videos += 1
                print(f"Debug - Vídeo '{video_name}' CONCLUÍDO (percentage={percentage:.2f}%)")
            else:
                print(f"Debug - Vídeo '{video_name}' NÃO concluído (percentage={percentage:.2f}%)")
    
    completion = int((completed_videos / total_videos) * 100)
    print(f"Debug - Tópico '{topic}': {completed_videos}/{total_videos} vídeos concluídos = {completion}%")
    return completion
