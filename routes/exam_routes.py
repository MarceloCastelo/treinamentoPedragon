# -*- coding: utf-8 -*-
"""
Rotas para gerenciamento de provas
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from .middleware import login_required, profile_complete_required, get_current_user, get_current_username
from .database import get_exam_results, save_exam_result, get_user_exam_attempts
from .config import VIDEOS_DIR
import os
import json
from datetime import datetime

# Criação do blueprint
exam_bp = Blueprint('exam', __name__)


def load_exam_data(topic_name):
    """Carrega os dados da prova de um tópico específico"""
    exam_path = os.path.join(VIDEOS_DIR, topic_name, 'prova.json')
    
    try:
        if os.path.exists(exam_path):
            with open(exam_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('prova', {})
        else:
            print(f"Arquivo de prova não encontrado: {exam_path}")
            return None
    except Exception as e:
        print(f"Erro ao carregar prova: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def check_exam_exists(topic_name):
    """Verifica se existe arquivo de prova para o tópico"""
    exam_path = os.path.join(VIDEOS_DIR, topic_name, 'prova.json')
    return os.path.exists(exam_path)


@exam_bp.route('/exam/<path:topic_name>')
@login_required
@profile_complete_required
def exam(topic_name):
    """Página de prova de um tópico específico"""
    from .progress_routes import calculate_topic_completion
    from .video_routes import get_all_topics
    
    user = get_current_user()
    username = get_current_username()
    
    # Verificar se existe prova para este tópico
    if not check_exam_exists(topic_name):
        flash('Não há prova disponível para este módulo.', 'info')
        return redirect(url_for('video.topic_detail', topic_name=topic_name))
    
    # Verificar se o curso foi concluído
    topics = get_all_topics()
    videos_count = len(topics.get(topic_name, []))
    completion = calculate_topic_completion(username, topic_name, videos_count)
    
    if completion < 100:
        flash(f'Você precisa completar todos os vídeos do módulo antes de fazer a prova. Progresso atual: {completion}%', 'warning')
        return redirect(url_for('video.topic_detail', topic_name=topic_name))
    
    # Carregar dados da prova
    exam_data = load_exam_data(topic_name)
    
    if not exam_data or 'questoes' not in exam_data:
        flash('Erro ao carregar a prova. Por favor, tente novamente.', 'error')
        return redirect(url_for('video.topic_detail', topic_name=topic_name))
    
    # Verificar tentativas anteriores no banco
    tentativas = get_user_exam_attempts(username, topic_name)
    num_tentativas = len(tentativas)
    previous_attempt = tentativas[-1] if tentativas else None
    
    # Limitar a 2 tentativas
    if num_tentativas >= 2:
        flash('Você já atingiu o limite de 2 tentativas para esta prova.', 'warning')
        return redirect(url_for('exam.exam_result', topic_name=topic_name))
    
    return render_template(
        'exam.html',
        user=user,
        topic_name=topic_name,
        questoes=exam_data['questoes'],
        previous_attempt=previous_attempt,
        num_tentativas=num_tentativas,
        max_tentativas=2
    )


@exam_bp.route('/submit-exam/<path:topic_name>', methods=['POST'])
@login_required
@profile_complete_required
def submit_exam(topic_name):
    """Processa o envio da prova e calcula a nota"""
    from .progress_routes import calculate_topic_completion
    from .video_routes import get_all_topics
    
    user = get_current_user()
    username = get_current_username()
    
    # Verificar se o curso foi concluído
    topics = get_all_topics()
    videos_count = len(topics.get(topic_name, []))
    completion = calculate_topic_completion(username, topic_name, videos_count)
    
    if completion < 100:
        return jsonify({
            'success': False,
            'error': f'Você precisa completar todos os vídeos do módulo antes de fazer a prova. Progresso atual: {completion}%'
        }), 403
    
    try:
        # Carregar dados da prova
        exam_data = load_exam_data(topic_name)
        
        if not exam_data or 'questoes' not in exam_data:
            return jsonify({
                'success': False,
                'error': 'Erro ao carregar dados da prova'
            }), 400
        
        # Obter respostas do usuário
        respostas_usuario = request.json.get('respostas', {})
        
        # Calcular nota
        total_questoes = len(exam_data['questoes'])
        acertos = 0
        resultados_detalhados = []
        
        for questao in exam_data['questoes']:
            numero = str(questao['numero'])
            tipo = questao.get('tipo', 'multipla_escolha')
            
            # Processar de acordo com o tipo de questão
            if tipo == 'correspondencia':
                # Questão de correspondência
                resposta_usuario = respostas_usuario.get(numero, [])
                itens = questao.get('itens_correspondencia', [])
                
                # Verificar se todas as correspondências estão corretas
                acertou = True
                if isinstance(resposta_usuario, list) and len(resposta_usuario) == len(itens):
                    for i, item in enumerate(itens):
                        resposta_correta = item['resposta_correta'].strip().lower()
                        resposta_dada = resposta_usuario[i].strip().lower() if i < len(resposta_usuario) else ''
                        if resposta_correta != resposta_dada:
                            acertou = False
                            break
                else:
                    acertou = False
                
                if acertou:
                    acertos += 1
                
                # Formatar respostas para exibição
                respostas_formatadas = []
                for i, item in enumerate(itens):
                    resp_usuario = resposta_usuario[i] if isinstance(resposta_usuario, list) and i < len(resposta_usuario) else ''
                    respostas_formatadas.append({
                        'descricao': item['descricao'],
                        'resposta_usuario': resp_usuario,
                        'resposta_correta': item['resposta_correta']
                    })
                
                resultados_detalhados.append({
                    'numero': questao['numero'],
                    'tipo': tipo,
                    'enunciado': questao['enunciado'],
                    'itens': respostas_formatadas,
                    'acertou': acertou,
                    'feedback': questao.get('feedback', '')
                })
            else:
                # Questões de verdadeiro/falso ou múltipla escolha
                resposta_usuario = respostas_usuario.get(numero, '')
                resposta_correta = questao.get('resposta_correta', '')
                
                acertou = str(resposta_usuario).strip() == str(resposta_correta).strip()
                if acertou:
                    acertos += 1
                
                resultados_detalhados.append({
                    'numero': questao['numero'],
                    'tipo': tipo,
                    'enunciado': questao['enunciado'],
                    'resposta_usuario': resposta_usuario,
                    'resposta_correta': resposta_correta,
                    'acertou': acertou,
                    'feedback': questao.get('feedback', ''),
                    'opcoes': questao.get('opcoes', {})
                })
        
        nota = (acertos / total_questoes) * 100
        aprovado = nota >= 70  # 70% para aprovação
        
        # Salvar resultado no banco de dados
        save_exam_result(
            username=username,
            topic=topic_name,
            score=nota,
            total_questions=total_questoes,
            correct_answers=acertos,
            answers={
                'aprovado': aprovado,
                'resultados': resultados_detalhados
            },
            time_taken=0
        )
        
        return jsonify({
            'success': True,
            'nota': nota,
            'acertos': acertos,
            'total': total_questoes,
            'aprovado': aprovado,
            'resultados': resultados_detalhados
        })
        
    except Exception as e:
        print(f"Erro ao processar prova: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@exam_bp.route('/exam-result/<path:topic_name>')
@login_required
@profile_complete_required
def exam_result(topic_name):
    """Página de resultado da prova"""
    user = get_current_user()
    username = get_current_username()
    
    # Carregar resultado do usuário do banco
    tentativas = get_user_exam_attempts(username, topic_name)
    
    if not tentativas:
        flash('Você ainda não fez esta prova.', 'info')
        return redirect(url_for('exam.exam', topic_name=topic_name))
    
    exam_result = tentativas[-1]
    num_tentativas = len(tentativas)
    
    # Formatar resultado para compatibilidade com template
    exam_result['nota'] = exam_result['score']
    exam_result['acertos'] = exam_result['correct_answers']
    exam_result['total'] = exam_result['total_questions']
    exam_result['data'] = exam_result['exam_date']
    if exam_result.get('answers'):
        exam_result['aprovado'] = exam_result['answers'].get('aprovado', False)
        exam_result['resultados'] = exam_result['answers'].get('resultados', [])
    else:
        exam_result['aprovado'] = exam_result['score'] >= 70
    
    return render_template(
        'exam_result.html',
        user=user,
        topic_name=topic_name,
        result=exam_result,
        num_tentativas=num_tentativas,
        max_tentativas=2,
        pode_ver_respostas=(num_tentativas >= 2 or exam_result.get('aprovado', False))
    )
