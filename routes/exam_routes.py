# -*- coding: utf-8 -*-
"""
Rotas para gerenciamento de provas
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file, make_response
from .middleware import login_required, profile_complete_required, get_current_user, get_current_username
from .database import get_exam_results, save_exam_result, get_user_exam_attempts
from .config import VIDEOS_DIR
import os
import json
from datetime import datetime
from io import BytesIO

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
    previous_attempt = None
    
    if tentativas:
        # Formatar tentativa anterior para compatibilidade com template
        last_attempt = tentativas[-1]
        previous_attempt = {
            'nota': last_attempt['score'],
            'acertos': last_attempt['correct_answers'],
            'total': last_attempt['total_questions'],
            'data': last_attempt['exam_date']
        }
    
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


@exam_bp.route('/download-certificate/<path:topic_name>')
@login_required
@profile_complete_required
def download_certificate(topic_name):
    """Gera e retorna o certificado digital em PDF para o aluno aprovado"""
    from .database import get_user

    user = get_current_user()
    username = get_current_username()

    # Verificar se o usuário foi aprovado nesta prova
    tentativas = get_user_exam_attempts(username, topic_name)
    if not tentativas:
        flash('Você ainda não realizou esta prova.', 'info')
        return redirect(url_for('exam.exam_result', topic_name=topic_name))

    # Verificar se existe alguma tentativa aprovada
    aprovado = any(t.get('score', 0) >= 70 for t in tentativas)
    if not aprovado:
        flash('Você precisa ser aprovado na prova para baixar o certificado.', 'warning')
        return redirect(url_for('exam.exam_result', topic_name=topic_name))

    # Pegar a tentativa aprovada (maior nota)
    melhor_tentativa = max(tentativas, key=lambda t: t.get('score', 0))

    # Nome completo do aluno (displayName do LDAP)
    nome_aluno = user.get('displayName', username) if user else username

    # Dados adicionais do usuário no BD
    user_db = get_user(username) or {}
    empresa = user_db.get('empresa', '')
    unidade = user_db.get('unidade', '')
    cargo = user_db.get('cargo', '')

    # Data de conclusão
    data_conclusao = melhor_tentativa.get('exam_date', datetime.now().strftime('%d/%m/%Y'))
    if hasattr(data_conclusao, 'strftime'):
        data_conclusao = data_conclusao.strftime('%d/%m/%Y')
    else:
        # Tentar converter string ISO para data formatada
        try:
            dt = datetime.fromisoformat(str(data_conclusao).replace('Z', ''))
            data_conclusao = dt.strftime('%d de %B de %Y')
        except Exception:
            data_conclusao = str(data_conclusao)[:10] if data_conclusao else datetime.now().strftime('%d/%m/%Y')

    nota = melhor_tentativa.get('score', 0)

    pdf_buffer = _gerar_certificado_pdf(
        nome_aluno=nome_aluno,
        topic_name=topic_name,
        data_conclusao=data_conclusao,
        nota=nota,
        empresa=empresa,
        unidade=unidade,
        cargo=cargo
    )

    nome_arquivo = f"certificado_{topic_name.replace(' ', '_').replace('/', '-')}.pdf"

    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    return response


def _gerar_certificado_pdf(nome_aluno, topic_name, data_conclusao, nota, empresa='', unidade='', cargo=''):
    """Gera o PDF do certificado e retorna um BytesIO"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        # reportlab não instalado
        buf = BytesIO(b"%PDF-1.4\n% reportlab nao instalado")
        buf.seek(0)
        return buf

    # Dimensões landscape A4
    PAGE_W, PAGE_H = landscape(A4)  # 841.89 x 595.28 pt

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # ─── Fundo azul escuro ────────────────────────────────────────────────────
    AZUL_ESCURO  = colors.HexColor('#032B56')
    AZUL_MEDIO   = colors.HexColor('#1e40af')
    AZUL_CLARO   = colors.HexColor('#3b82f6')
    AZUL_BG2     = colors.HexColor('#0f3d7a')
    BRANCO       = colors.white
    DOURADO      = colors.HexColor('#f59e0b')

    # Fundo
    c.setFillColor(AZUL_ESCURO)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Faixa decorativa lateral esquerda
    c.setFillColor(AZUL_MEDIO)
    c.rect(0, 0, 1.2*cm, PAGE_H, fill=1, stroke=0)

    # Faixa decorativa lateral direita
    c.rect(PAGE_W - 1.2*cm, 0, 1.2*cm, PAGE_H, fill=1, stroke=0)

    # Faixa decorativa superior
    c.rect(0, PAGE_H - 1.2*cm, PAGE_W, 1.2*cm, fill=1, stroke=0)

    # Faixa decorativa inferior
    c.rect(0, 0, PAGE_W, 1.2*cm, fill=1, stroke=0)

    # Borda interna dourada
    c.setStrokeColor(DOURADO)
    c.setLineWidth(1.5)
    c.rect(1.8*cm, 1.8*cm, PAGE_W - 3.6*cm, PAGE_H - 3.6*cm, fill=0, stroke=1)

    # Borda pontilhada interna fina
    c.setStrokeColor(colors.HexColor('#93c5fd'))
    c.setLineWidth(0.5)
    c.setDash(4, 4)
    c.rect(2.4*cm, 2.4*cm, PAGE_W - 4.8*cm, PAGE_H - 4.8*cm, fill=0, stroke=1)
    c.setDash()

    # Ornamentos nos cantos
    for cx, cy in [(2.2*cm, 2.2*cm), (PAGE_W - 2.2*cm, 2.2*cm),
                   (2.2*cm, PAGE_H - 2.2*cm), (PAGE_W - 2.2*cm, PAGE_H - 2.2*cm)]:
        c.setFillColor(DOURADO)
        c.circle(cx, cy, 3, fill=1, stroke=0)

    # ─── Logo da empresa ──────────────────────────────────────────────────────
    logo_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'static', 'images', 'logos', 'ADTSA - LOGOMARCA.png'
    )
    logo_branca_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'static', 'images', 'logos', 'ADTSA - BRANCA.png'
    )
    logo_usar = logo_branca_path if os.path.exists(logo_branca_path) else logo_path
    if os.path.exists(logo_usar):
        try:
            logo_w = 5.5*cm
            logo_h = 2.0*cm
            logo_x = (PAGE_W - logo_w) / 2
            logo_y = PAGE_H - 4.5*cm
            c.drawImage(logo_usar, logo_x, logo_y, width=logo_w, height=logo_h,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # ─── Textos ───────────────────────────────────────────────────────────────
    center_x = PAGE_W / 2

    # "CERTIFICADO DE CONCLUSÃO"
    c.setFillColor(DOURADO)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(center_x, PAGE_H - 6.5*cm, "CERTIFICADO DE CONCLUSÃO")

    # Linha separadora dourada
    c.setStrokeColor(DOURADO)
    c.setLineWidth(1.2)
    c.line(center_x - 8*cm, PAGE_H - 6.9*cm, center_x + 8*cm, PAGE_H - 6.9*cm)

    # "Certificamos que"
    c.setFillColor(colors.HexColor('#bfdbfe'))
    c.setFont("Helvetica", 13)
    c.drawCentredString(center_x, PAGE_H - 8.0*cm, "Certificamos que")

    # Nome do aluno
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 24)
    # Se o nome for muito longo, reduzir fonte
    nome_font = 24
    while c.stringWidth(nome_aluno, "Helvetica-Bold", nome_font) > PAGE_W - 8*cm and nome_font > 14:
        nome_font -= 1
    c.setFont("Helvetica-Bold", nome_font)
    c.drawCentredString(center_x, PAGE_H - 9.5*cm, nome_aluno.upper())

    # Linha sob o nome
    c.setStrokeColor(colors.HexColor('#60a5fa'))
    c.setLineWidth(0.8)
    nome_w = c.stringWidth(nome_aluno.upper(), "Helvetica-Bold", nome_font)
    c.line(center_x - nome_w/2, PAGE_H - 9.8*cm, center_x + nome_w/2, PAGE_H - 9.8*cm)

    # Texto do módulo
    c.setFillColor(colors.HexColor('#bfdbfe'))
    c.setFont("Helvetica", 13)
    c.drawCentredString(center_x, PAGE_H - 10.8*cm,
                        "concluiu com aprovação o módulo de treinamento:")

    # Nome do módulo
    c.setFillColor(AZUL_CLARO)
    topic_font = 17
    while c.stringWidth(topic_name, "Helvetica-Bold", topic_font) > PAGE_W - 6*cm and topic_font > 11:
        topic_font -= 1
    c.setFont("Helvetica-Bold", topic_font)
    c.drawCentredString(center_x, PAGE_H - 11.9*cm, topic_name)

    # Nota
    c.setFillColor(colors.HexColor('#86efac'))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(center_x, PAGE_H - 12.9*cm,
                        f"Nota obtida: {nota:.1f}%")

    # Empresa/Unidade do colaborador (se disponível)
    if empresa or unidade:
        info_parts = []
        if empresa:
            info_parts.append(empresa)
        if unidade:
            info_parts.append(unidade)
        if cargo:
            info_parts.append(cargo)
        c.setFillColor(colors.HexColor('#94a3b8'))
        c.setFont("Helvetica", 10)
        c.drawCentredString(center_x, PAGE_H - 13.7*cm, " | ".join(info_parts))

    # Data na parte inferior
    c.setFillColor(colors.HexColor('#bfdbfe'))
    c.setFont("Helvetica", 11)
    c.drawCentredString(center_x, 3.6*cm, f"Emitido em {data_conclusao}")

    # Texto institucional
    c.setFillColor(colors.HexColor('#64748b'))
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(center_x, 2.5*cm,
                        "GRUPO ADTSA — Divisão de Concessionárias — Plataforma de Treinamento Corporativo")

    c.save()
    buffer.seek(0)
    return buffer


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
