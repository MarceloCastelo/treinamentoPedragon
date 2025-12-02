"""
Pacote de rotas modularizadas
"""
from .auth_routes import auth_bp
from .video_routes import video_bp
from .progress_routes import progress_bp
from .user_routes import user_bp
from .exam_routes import exam_bp

__all__ = ['auth_bp', 'video_bp', 'progress_bp', 'user_bp', 'exam_bp']
