#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige os topics da tabela exam_results que ainda usam o formato antigo (sem categoria).
Faz o mapeamento buscando a pasta real em /app/videos.
"""
import sys, os
sys.path.insert(0, '/app')
from routes.database import execute_query

VIDEOS_DIR = '/app/videos'


def build_topic_map():
    """Mapeia nome_do_curso -> categoria/nome_do_curso a partir das pastas reais."""
    mapping = {}
    for cat in os.listdir(VIDEOS_DIR):
        cat_path = os.path.join(VIDEOS_DIR, cat)
        if not os.path.isdir(cat_path):
            continue
        for course in os.listdir(cat_path):
            course_path = os.path.join(cat_path, course)
            if os.path.isdir(course_path):
                full_key = f"{cat}/{course}"
                # Mapeia o nome do curso diretamente para o caminho completo
                mapping[course] = full_key
    return mapping


def fix_double_encoding(s):
    try:
        fixed = s.encode('latin-1').decode('utf-8')
        return fixed if fixed != s else None
    except Exception:
        return None


topic_map = build_topic_map()
print('Mapa de cursos disponivel:')
for k, v in sorted(topic_map.items()):
    print(f'  {repr(k)} -> {repr(v)}')
print()

# Busca todos os topics distintos em exam_results
rows = execute_query('SELECT DISTINCT topic FROM exam_results ORDER BY topic')
print('=== Topics em exam_results ===')
for r in rows:
    old = r['topic']

    # 1. Tenta corrigir double-encoding primeiro
    maybe_encoded = fix_double_encoding(old)
    base = maybe_encoded if maybe_encoded else old

    # 2. Se já tem '/', provavelmente já está no formato novo
    if '/' in base:
        # Apenas corrige double-encoding se necessário
        if maybe_encoded and maybe_encoded != old:
            count = execute_query(
                'SELECT COUNT(*) as n FROM exam_results WHERE topic = :t', {'t': old}
            )[0]['n']
            execute_query(
                'UPDATE exam_results SET topic = :new WHERE topic = :old',
                {'new': maybe_encoded, 'old': old},
                fetch_all=False
            )
            print(f'  [ENCODING CORRIGIDO] {repr(old)} -> {repr(maybe_encoded)} ({count} registros)')
        else:
            exists = os.path.isdir(os.path.join(VIDEOS_DIR, base))
            status = 'OK' if exists else 'CAMINHO NAO ENCONTRADO'
            print(f'  [{status}] {repr(old)}')
        continue

    # 3. Tenta mapear pelo nome do curso para caminho completo
    new_topic = topic_map.get(base)
    if new_topic:
        count = execute_query(
            'SELECT COUNT(*) as n FROM exam_results WHERE topic = :t', {'t': old}
        )[0]['n']
        execute_query(
            'UPDATE exam_results SET topic = :new WHERE topic = :old',
            {'new': new_topic, 'old': old},
            fetch_all=False
        )
        print(f'  [CORRIGIDO] {repr(old)} -> {repr(new_topic)} ({count} registros)')
    else:
        print(f'  [SEM MAPEAMENTO] {repr(old)} - verifique manualmente')

print()
print('=== Validacao final ===')
rows = execute_query('SELECT DISTINCT topic FROM exam_results ORDER BY topic')
for r in rows:
    topic = r['topic']
    path_ok = os.path.isdir(os.path.join(VIDEOS_DIR, topic))
    print(f'  [{"OK" if path_ok else "ERRO"}] {repr(topic)}')
