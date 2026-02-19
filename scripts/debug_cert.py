#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')
from routes.database import execute_query, get_user_progress

# Exam results de clara.santos
rows = execute_query(
    'SELECT topic, score, exam_date FROM exam_results WHERE username = :u ORDER BY exam_date DESC',
    {'u': 'clara.santos'}
)
print('=== Exam results clara.santos ===')
for r in rows:
    print('  Topic:', repr(r['topic']), ' | Score:', r['score'])

print()

# Simular calculo do certificado para cada topic de prova
print('=== Simulacao do calculo de duracao no certificado ===')
for r in rows:
    topic = r['topic']
    progresso = get_user_progress('clara.santos', topic)
    topic_progress = progresso.get(topic, {})
    total_seg = sum(float(v.get('duration', 0)) for v in topic_progress.values())
    horas = total_seg / 3600
    print('  Topic:', repr(topic))
    print('    Videos com progresso:', len(topic_progress))
    print('    Total segundos:', round(total_seg, 1))
    print('    Total horas:', round(horas, 2))
    print()

# Verificar marcelo.castelo como referencia
print('=== Referencia: marcelo.castelo ===')
rows_m = execute_query(
    'SELECT DISTINCT topic FROM video_progress WHERE username = :u ORDER BY topic',
    {'u': 'marcelo.castelo'}
)
for r in rows_m:
    topic = r['topic']
    progresso = get_user_progress('marcelo.castelo', topic)
    tp = progresso.get(topic, {})
    total_seg = sum(float(v.get('duration', 0)) for v in tp.values())
    print('  Topic:', repr(topic), '|', len(tp), 'videos |', round(total_seg/3600, 2), 'h')
