#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir os caminhos de vídeos no banco de dados após mudança de pastas.
Corrige:
1. Caminhos sem categoria (antigos) -> com categoria/curso (novos)
2. Double-encoding de caracteres UTF-8 (ex: PeÃ§as -> Peças)
"""
import sys
import os

sys.path.insert(0, '/app')
from routes.database import execute_query

VIDEOS_DIR = '/app/videos'


def fix_double_encoding(s):
    """Tenta corrigir double-encoding latin-1 -> utf-8"""
    try:
        fixed = s.encode('latin-1').decode('utf-8')
        return fixed if fixed != s else None
    except Exception:
        return None


def validate_paths():
    rows = execute_query('SELECT DISTINCT topic FROM video_progress ORDER BY topic')
    ok = True
    for r in rows:
        topic = r['topic']
        path_ok = os.path.isdir(os.path.join(VIDEOS_DIR, topic))
        status = 'OK' if path_ok else 'ERRO'
        if not path_ok:
            ok = False
        print(f'  [{status}] {repr(topic)}')
    return ok


print('=== Correcao de double-encoding ===')
rows = execute_query('SELECT DISTINCT topic FROM video_progress ORDER BY topic')
for r in rows:
    old = r['topic']
    fixed = fix_double_encoding(old)
    if fixed:
        rowcount = execute_query(
            'UPDATE video_progress SET topic = :new WHERE topic = :old',
            {'new': fixed, 'old': old},
            fetch_all=False
        )
        print(f'  Atualizado {rowcount} registro(s): {repr(old)} -> {repr(fixed)}')

print()
print('=== Validacao final dos caminhos ===')
all_ok = validate_paths()

if all_ok:
    print()
    print('Todos os caminhos estao corretos!')
else:
    print()
    print('Ainda ha caminhos com erro. Verifique se as pastas existem no disco.')
