# -*- coding: utf-8 -*-
"""Teste da função format_video_name"""
import sys
import os
import re

# Configura UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Copia a função e o dicionário aqui
PALAVRA_CORRECOES = {
    'reimpressao': 'Reimpressão',
    'requisicao': 'Requisição',
    'manutencao': 'Manutenção',
    'marcacao': 'Marcação',
    'pecas': 'Peças',
    'peca': 'Peça',
}

def format_video_name(filename):
    """Formata o nome do arquivo de vídeo para exibição"""
    # Remove a extensão
    name = os.path.splitext(filename)[0]
    
    # Remove prefixo numérico (ex: 01_, 02_, etc)
    name = re.sub(r'^\d+_', '', name)
    
    # Substitui underscores por espaços
    name = name.replace('_', ' ')
    
    # Divide em palavras
    words = name.split()
    formatted_words = []
    small_words = ['de', 'do', 'da', 'dos', 'das', 'e', 'a', 'o', 'em', 'para', 'com', 'sem', 'por', 'ao', 'aos']
    
    for i, word in enumerate(words):
        word_lower = word.lower()
        
        # Verifica se a palavra precisa de correção de acentuação
        if word_lower in PALAVRA_CORRECOES:
            formatted_words.append(PALAVRA_CORRECOES[word_lower])
        # Primeira palavra sempre maiúscula
        elif i == 0 or word_lower not in small_words:
            formatted_words.append(word.capitalize())
        else:
            formatted_words.append(word_lower)
    
    return ' '.join(formatted_words)

# Testes
test_files = [
    '15_Dealernet_Workflow_-_Produtos_-_Reimpressao_de_requisicao_de_pecas.mp4',
    '03_Dealernet_Workflow_-_Produtos_-_Requisitar_Produtos_na_Boqueta.mp4',
    '02_Dealernet_Workflow_-_Oficina_-_Marcacao_de_tempo.mp4',
]

print("Testando função format_video_name:\n")
print("-" * 80)
for filename in test_files:
    formatted = format_video_name(filename)
    print(f"Original : {filename}")
    print(f"Formatado: {formatted}")
    print()
