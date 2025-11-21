"""
Configurações centralizadas da aplicação
"""
import os

# Diretório onde os vídeos estão armazenados
VIDEOS_DIR = r"/app/videos"

# Extensões de vídeo suportadas
VIDEO_EXTENSIONS = ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv']

# Arquivo de progresso dos vídeos
PROGRESS_FILE = 'video_progress.json'

# Porcentagem mínima para considerar um vídeo como assistido
WATCHED_THRESHOLD = 0.9  # 90%
