"""
Configurações centralizadas da aplicação
"""
import os

# Diretório onde os vídeos estão armazenados
VIDEOS_DIR = r"\\10.81.2.249\troca\Treinamento - Dealernet"

# Extensões de vídeo suportadas
VIDEO_EXTENSIONS = ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv']

# Arquivo de progresso dos vídeos
PROGRESS_FILE = 'video_progress.json'

# Porcentagem mínima para considerar um vídeo como assistido
WATCHED_THRESHOLD = 0.9  # 90%
