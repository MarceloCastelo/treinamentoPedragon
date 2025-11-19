# -*- coding: utf-8 -*-
"""Script para testar encoding dos nomes de arquivos"""
import os
import sys

# Configura UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

VIDEOS_DIR = r"\\10.81.2.249\troca\Treinamento - Dealernet"

print(f"Sistema: {sys.platform}")
print(f"Encoding padrão: {sys.getdefaultencoding()}")
print(f"Encoding do filesystem: {sys.getfilesystemencoding()}")
print(f"Encoding stdout: {sys.stdout.encoding}")
print("-" * 80)

if os.path.exists(VIDEOS_DIR):
    print(f"\nLendo diretório: {VIDEOS_DIR}\n")
    
    for topic_name in os.listdir(VIDEOS_DIR):
        topic_path = os.path.join(VIDEOS_DIR, topic_name)
        
        if os.path.isdir(topic_path):
            # Lista arquivos no tópico
            try:
                files = os.listdir(topic_path)
                for file_name in files:
                    if file_name.endswith(('.mp4', '.avi', '.mkv', '.mov')):
                        # Procura por arquivos com "requisicao" ou "reimpressao"
                        if 'requisi' in file_name.lower() or 'reimpres' in file_name.lower():
                            print(f"Tópico: {topic_name}")
                            print(f"  Vídeo: {file_name}")
                            print(f"    Tipo: {type(file_name)}")
                            print(f"    Repr: {repr(file_name)}")
                            print(f"    Bytes: {file_name.encode('utf-8')}")
                            print()
            except Exception as e:
                print(f"  Erro ao listar arquivos em {topic_name}: {e}")
else:
    print(f"Diretório não encontrado: {VIDEOS_DIR}")
