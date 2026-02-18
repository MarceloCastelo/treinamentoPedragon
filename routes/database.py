# -*- coding: utf-8 -*-
"""
Módulo de conexão e operações com banco de dados MySQL
"""
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import pymysql
from datetime import datetime
import json

# Configuração de conexão
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3308')
DB_NAME = os.getenv('DB_NAME', 'treinamento_adtsa')
DB_USER = os.getenv('DB_USER', 'adtsa_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'adtsa_pass123')

# String de conexão
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Engine e Session
engine = None
SessionLocal = None


def init_db():
    """Inicializa a conexão com o banco de dados"""
    global engine, SessionLocal
    
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            connect_args={
                'connect_timeout': 10,
                'charset': 'utf8mb4'
            }
        )
        
        SessionLocal = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        ))
        
        # Testa a conexão
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("✓ Conexão com MySQL estabelecida com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao conectar ao MySQL: {e}")
        return False


@contextmanager
def get_db():
    """Context manager para obter uma sessão do banco de dados"""
    if SessionLocal is None:
        init_db()
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    Executa uma query no banco de dados
    
    Args:
        query: SQL query string
        params: Parâmetros da query (dict)
        fetch_one: Se True, retorna apenas um resultado
        fetch_all: Se True, retorna todos os resultados
    
    Returns:
        Resultado da query ou None
    """
    try:
        with get_db() as session:
            result = session.execute(text(query), params or {})
            
            if fetch_one:
                row = result.fetchone()
                return dict(row._mapping) if row else None
            elif fetch_all:
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]
            else:
                session.commit()
                return result.rowcount
    except Exception as e:
        print(f"Erro ao executar query: {e}")
        return None


# ============= FUNÇÕES PARA USUÁRIOS =============

def get_user(username):
    """Obtém dados de um usuário"""
    query = "SELECT * FROM users WHERE username = :username"
    return execute_query(query, {'username': username}, fetch_one=True)


def create_or_update_user(username, email=None, phone=None, department=None, position=None, empresa=None, marca=None, unidade=None, setor=None, cargo=None, selected_courses=None, preserve_existing=False):
    """Cria ou atualiza um usuário
    
    Args:
        preserve_existing: Se True, apenas atualiza campos não-None, preservando valores existentes
    """
    # Converte selected_courses para JSON se for uma lista
    if selected_courses and isinstance(selected_courses, list):
        selected_courses = json.dumps(selected_courses)
    
    if preserve_existing:
        # Busca dados existentes e preserva campos não fornecidos
        existing_user = get_user(username)
        if existing_user:
            email = email if email is not None else existing_user.get('email')
            phone = phone if phone is not None else existing_user.get('phone')
            department = department if department is not None else existing_user.get('department')
            position = position if position is not None else existing_user.get('position')
            empresa = empresa if empresa is not None else existing_user.get('empresa')
            marca = marca if marca is not None else existing_user.get('marca')
            unidade = unidade if unidade is not None else existing_user.get('unidade')
            setor = setor if setor is not None else existing_user.get('setor')
            cargo = cargo if cargo is not None else existing_user.get('cargo')
            # Para selected_courses, preserva apenas se não foi fornecido
            if selected_courses is None and existing_user.get('selected_courses'):
                selected_courses = existing_user.get('selected_courses')
    
    query = """
        INSERT INTO users (username, email, phone, department, position, empresa, marca, unidade, setor, cargo, selected_courses)
        VALUES (:username, :email, :phone, :department, :position, :empresa, :marca, :unidade, :setor, :cargo, :selected_courses)
        ON DUPLICATE KEY UPDATE
            email = :email,
            phone = :phone,
            department = :department,
            position = :position,
            empresa = :empresa,
            marca = :marca,
            unidade = :unidade,
            setor = :setor,
            cargo = :cargo,
            selected_courses = :selected_courses,
            updated_at = CURRENT_TIMESTAMP
    """
    params = {
        'username': username,
        'email': email,
        'phone': phone,
        'department': department,
        'position': position,
        'empresa': empresa,
        'marca': marca,
        'unidade': unidade,
        'setor': setor,
        'cargo': cargo,
        'selected_courses': selected_courses
    }
    return execute_query(query, params, fetch_all=False)


def get_all_users():
    """Obtém todos os usuários"""
    query = "SELECT * FROM users ORDER BY username"
    return execute_query(query)


def update_profile_picture(username, filename):
    """Atualiza o campo profile_picture do usuário"""
    query = """
        UPDATE users SET profile_picture = :filename, updated_at = CURRENT_TIMESTAMP
        WHERE username = :username
    """
    return execute_query(query, {'username': username, 'filename': filename}, fetch_all=False)


# ============= FUNÇÕES PARA PROGRESSO DE VÍDEOS =============

def get_user_progress(username, topic=None):
    """
    Obtém o progresso de vídeos de um usuário
    
    Args:
        username: Nome do usuário
        topic: Tópico específico (opcional)
    
    Returns:
        Dict com progresso organizado por tópico e vídeo
    """
    if topic:
        query = """
            SELECT * FROM video_progress 
            WHERE username = :username AND topic = :topic
            ORDER BY last_watched DESC
        """
        params = {'username': username, 'topic': topic}
    else:
        query = """
            SELECT * FROM video_progress 
            WHERE username = :username
            ORDER BY last_watched DESC
        """
        params = {'username': username}
    
    results = execute_query(query, params)
    
    # Organiza os resultados em formato compatível com o código existente
    progress_dict = {}
    if results:
        for row in results:
            topic_name = row['topic']
            video_name = row['video_name']
            
            if topic_name not in progress_dict:
                progress_dict[topic_name] = {}
            
            progress_dict[topic_name][video_name] = {
                'current_time': float(row['current_time_seconds']),
                'duration': float(row['duration_seconds']),
                'last_watched': row['last_watched'].isoformat() if row['last_watched'] else None
            }
    
    return progress_dict


def save_video_progress(username, topic, video_name, current_time, duration):
    """Salva ou atualiza o progresso de um vídeo"""
    query = """
        INSERT INTO video_progress (username, topic, video_name, current_time_seconds, duration_seconds, last_watched)
        VALUES (:username, :topic, :video_name, :current_time, :duration, NOW())
        ON DUPLICATE KEY UPDATE
            current_time_seconds = VALUES(current_time_seconds),
            duration_seconds = VALUES(duration_seconds),
            last_watched = NOW()
    """
    params = {
        'username': username,
        'topic': topic,
        'video_name': video_name,
        'current_time': current_time,
        'duration': duration
    }
    return execute_query(query, params, fetch_all=False)


def get_topic_view_counts():
    """
    Retorna a contagem de visualizações por tópico.
    Define 'visualização' como: o usuário assistiu >= 10% do vídeo.
    Retorna lista de dicts ordenada por views desc: [{topic, views, unique_users}]
    """
    query = """
        SELECT
            topic,
            COUNT(*) AS views,
            COUNT(DISTINCT username) AS unique_users
        FROM video_progress
        WHERE duration_seconds > 0
          AND (current_time_seconds / duration_seconds) >= 0.10
        GROUP BY topic
        ORDER BY views DESC
    """
    results = execute_query(query)
    return results if results else []


def get_video_view_counts():
    """
    Retorna a contagem de visualizações por vídeo individual.
    Define 'visualização' como: o usuário assistiu >= 10% do vídeo.
    Retorna lista de dicts ordenada por views desc: [{topic, video_name, views, unique_users}]
    """
    query = """
        SELECT
            topic,
            video_name,
            COUNT(*) AS views,
            COUNT(DISTINCT username) AS unique_users
        FROM video_progress
        WHERE duration_seconds > 0
          AND (current_time_seconds / duration_seconds) >= 0.10
        GROUP BY topic, video_name
        ORDER BY views DESC
    """
    results = execute_query(query)
    return results if results else []


def get_all_progress():
    """Obtém o progresso de todos os usuários"""
    query = "SELECT * FROM video_progress ORDER BY username, topic, video_name"
    results = execute_query(query)
    
    # Organiza em formato compatível: {username: {topic: {video: progress}}}
    all_progress = {}
    if results:
        for row in results:
            username = row['username']
            topic = row['topic']
            video_name = row['video_name']
            
            if username not in all_progress:
                all_progress[username] = {}
            if topic not in all_progress[username]:
                all_progress[username][topic] = {}
            
            all_progress[username][topic][video_name] = {
                'current_time': float(row['current_time_seconds']),
                'duration': float(row['duration_seconds']),
                'last_watched': row['last_watched'].isoformat() if row['last_watched'] else None
            }
    
    return all_progress


def get_topic_progress_stats(username, topic):
    """Obtém estatísticas de progresso de um tópico"""
    query = """
        SELECT 
            COUNT(*) as total_videos,
            SUM(CASE WHEN current_time_seconds >= duration_seconds * 0.9 THEN 1 ELSE 0 END) as completed_videos
        FROM video_progress
        WHERE username = :username AND topic = :topic AND duration_seconds > 0
    """
    return execute_query(query, {'username': username, 'topic': topic}, fetch_one=True)


# ============= FUNÇÕES PARA RESULTADOS DE PROVAS =============

def save_exam_result(username, topic, score, total_questions, correct_answers, answers=None, time_taken=0):
    """Salva o resultado de uma prova"""
    query = """
        INSERT INTO exam_results 
        (username, topic, score, total_questions, correct_answers, answers, time_taken, exam_date)
        VALUES (:username, :topic, :score, :total_questions, :correct_answers, :answers, :time_taken, NOW())
    """
    params = {
        'username': username,
        'topic': topic,
        'score': score,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'answers': json.dumps(answers) if answers else None,
        'time_taken': time_taken
    }
    return execute_query(query, params, fetch_all=False)


def get_exam_results(username=None, topic=None):
    """
    Obtém resultados de provas
    
    Args:
        username: Usuário específico (opcional)
        topic: Tópico específico (opcional)
    
    Returns:
        Dict organizado por usuário e tópico
    """
    conditions = []
    params = {}
    
    if username:
        conditions.append("username = :username")
        params['username'] = username
    
    if topic:
        conditions.append("topic = :topic")
        params['topic'] = topic
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"""
        SELECT * FROM exam_results 
        WHERE {where_clause}
        ORDER BY exam_date DESC
    """
    
    results = execute_query(query, params)
    
    # Organiza em formato compatível: {username: {topic: [resultados]}}
    exam_dict = {}
    if results:
        for row in results:
            user = row['username']
            topic_name = row['topic']
            
            if user not in exam_dict:
                exam_dict[user] = {}
            if topic_name not in exam_dict[user]:
                exam_dict[user][topic_name] = []
            
            exam_dict[user][topic_name].append({
                'score': float(row['score']),
                'total_questions': row['total_questions'],
                'correct_answers': row['correct_answers'],
                'exam_date': row['exam_date'].isoformat() if row['exam_date'] else None,
                'time_taken': row['time_taken'],
                'answers': json.loads(row['answers']) if row['answers'] else None
            })
    
    return exam_dict


def get_user_exam_attempts(username, topic):
    """Obtém todas as tentativas de prova de um usuário em um tópico"""
    query = """
        SELECT * FROM exam_results 
        WHERE username = :username AND topic = :topic
        ORDER BY exam_date DESC
    """
    results = execute_query(query, {'username': username, 'topic': topic})
    
    if results:
        return [{
            'score': float(row['score']),
            'total_questions': row['total_questions'],
            'correct_answers': row['correct_answers'],
            'exam_date': row['exam_date'].isoformat() if row['exam_date'] else None,
            'time_taken': row['time_taken'],
            'answers': json.loads(row['answers']) if row['answers'] else None
        } for row in results]
    
    return []


def get_best_exam_score(username, topic):
    """Obtém a melhor nota de um usuário em um tópico"""
    query = """
        SELECT MAX(score) as best_score
        FROM exam_results
        WHERE username = :username AND topic = :topic
    """
    result = execute_query(query, {'username': username, 'topic': topic}, fetch_one=True)
    return result['best_score'] if result and result['best_score'] else 0


# ============= FUNÇÕES DE AUDITORIA =============

def log_action(username, action, details=None, ip_address=None):
    """Registra uma ação no log de auditoria"""
    query = """
        INSERT INTO audit_log (username, action, details, ip_address)
        VALUES (:username, :action, :details, :ip_address)
    """
    params = {
        'username': username,
        'action': action,
        'details': details,
        'ip_address': ip_address
    }
    return execute_query(query, params, fetch_all=False)


# ============= FUNÇÕES DE SESSÕES ATIVAS =============

def register_session(session_id, username, ip_address=None, user_agent=None):
    """
    Registra uma nova sessão ativa no banco de dados
    Remove outras sessões antigas do mesmo usuário para evitar duplicação
    
    Args:
        session_id: ID único da sessão
        username: Nome do usuário
        ip_address: Endereço IP do usuário
        user_agent: User agent do navegador
    
    Returns:
        Número de linhas afetadas
    """
    try:
        # Primeiro, remove qualquer sessão antiga deste usuário
        cleanup_query = """
            DELETE FROM active_sessions 
            WHERE username = :username AND session_id != :session_id
        """
        execute_query(cleanup_query, {'username': username, 'session_id': session_id}, fetch_all=False)
        
        # Agora insere/atualiza a sessão atual
        query = """
            INSERT INTO active_sessions (session_id, username, login_time, last_activity, ip_address, user_agent)
            VALUES (:session_id, :username, NOW(), NOW(), :ip_address, :user_agent)
            ON DUPLICATE KEY UPDATE
                last_activity = NOW(),
                ip_address = VALUES(ip_address),
                user_agent = VALUES(user_agent)
        """
        params = {
            'session_id': session_id,
            'username': username,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        result = execute_query(query, params, fetch_all=False)
        print(f"✓ Sessão registrada: {username} (session_id: {session_id[:8]}...)")
        return result
    except Exception as e:
        print(f"✗ Erro ao registrar sessão para {username}: {e}")
        return None


def update_session_activity(session_id):
    """
    Atualiza o timestamp de última atividade de uma sessão
    
    Args:
        session_id: ID único da sessão
    
    Returns:
        Número de linhas afetadas
    """
    query = """
        UPDATE active_sessions 
        SET last_activity = NOW()
        WHERE session_id = :session_id
    """
    return execute_query(query, {'session_id': session_id}, fetch_all=False)


def remove_session(session_id):
    """
    Remove uma sessão do banco de dados (logout)
    
    Args:
        session_id: ID único da sessão
    
    Returns:
        Número de linhas afetadas
    """
    query = "DELETE FROM active_sessions WHERE session_id = :session_id"
    return execute_query(query, {'session_id': session_id}, fetch_all=False)


def get_active_users(timeout_minutes=30):
    """
    Obtém lista de usuários atualmente logados (uma entrada por usuário)
    Remove automaticamente sessões expiradas antes de buscar
    
    Args:
        timeout_minutes: Tempo em minutos para considerar uma sessão inativa (padrão: 30)
    
    Returns:
        Lista de dicionários com informações dos usuários ativos únicos
    """
    # Primeiro limpa sessões inativas
    cleanup_inactive_sessions(timeout_minutes)
    
    # Busca apenas a sessão mais recente de cada usuário
    query = """
        SELECT 
            s.session_id,
            s.username,
            s.login_time,
            s.last_activity,
            s.ip_address,
            s.user_agent,
            u.email,
            u.department,
            u.position,
            TIMESTAMPDIFF(MINUTE, s.last_activity, NOW()) as inactive_minutes
        FROM active_sessions s
        INNER JOIN (
            SELECT username, MAX(last_activity) as max_activity
            FROM active_sessions
            WHERE TIMESTAMPDIFF(MINUTE, last_activity, NOW()) < :timeout_minutes
            GROUP BY username
        ) latest ON s.username = latest.username AND s.last_activity = latest.max_activity
        LEFT JOIN users u ON s.username = u.username
        ORDER BY s.last_activity DESC
    """
    return execute_query(query, {'timeout_minutes': timeout_minutes})


def get_user_sessions(username):
    """
    Obtém todas as sessões ativas de um usuário específico
    
    Args:
        username: Nome do usuário
    
    Returns:
        Lista de sessões ativas do usuário
    """
    query = """
        SELECT session_id, login_time, last_activity, ip_address, user_agent
        FROM active_sessions
        WHERE username = :username
        ORDER BY last_activity DESC
    """
    return execute_query(query, {'username': username})


def cleanup_inactive_sessions(timeout_minutes=30):
    """
    Remove sessões inativas do banco de dados
    
    Args:
        timeout_minutes: Tempo em minutos para considerar uma sessão inativa (padrão: 30)
    
    Returns:
        Número de sessões removidas
    """
    query = """
        DELETE FROM active_sessions
        WHERE TIMESTAMPDIFF(MINUTE, last_activity, NOW()) >= :timeout_minutes
    """
    return execute_query(query, {'timeout_minutes': timeout_minutes}, fetch_all=False)


def get_active_users_count(timeout_minutes=30):
    """
    Obtém o número de usuários atualmente logados
    Remove automaticamente sessões expiradas antes de contar
    
    Args:
        timeout_minutes: Tempo em minutos para considerar uma sessão inativa (padrão: 30)
    
    Returns:
        Número de usuários ativos (sessões ativas)
    """
    # Primeiro limpa sessões inativas
    cleanup_inactive_sessions(timeout_minutes)
    
    query = """
        SELECT COUNT(DISTINCT username) as active_count
        FROM active_sessions
        WHERE TIMESTAMPDIFF(MINUTE, last_activity, NOW()) < :timeout_minutes
    """
    result = execute_query(query, {'timeout_minutes': timeout_minutes}, fetch_one=True)
    return result['active_count'] if result else 0


def get_session_info(session_id):
    """
    Obtém informações de uma sessão específica
    
    Args:
        session_id: ID único da sessão
    
    Returns:
        Dicionário com informações da sessão ou None
    """
    query = """
        SELECT * FROM active_sessions
        WHERE session_id = :session_id
    """
    return execute_query(query, {'session_id': session_id}, fetch_one=True)


# Inicializa o banco ao importar o módulo
init_db()
