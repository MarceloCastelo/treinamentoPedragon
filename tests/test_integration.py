"""
Script de teste para verificar a integração dos módulos
"""

def test_imports():
    """Testa se todas as importações estão funcionando"""
    try:
        # Testar importação dos blueprints
        from routes import auth_bp, video_bp, progress_bp, user_bp
        print("✅ Blueprints importados com sucesso")
        
        # Testar importação de funções auxiliares
        from routes.video_routes import format_video_name
        from routes.middleware import login_required, get_current_user
        from routes.ldap_service import authenticate_ldap
        print("✅ Funções auxiliares importadas com sucesso")
        
        # Testar importação de configurações
        from routes.config import VIDEOS_DIR, VIDEO_EXTENSIONS
        print("✅ Configurações importadas com sucesso")
        
        # Testar funções de progresso
        from routes.progress_routes import load_progress, save_progress
        print("✅ Funções de progresso importadas com sucesso")
        
        print("\n✨ Todos os testes de integração passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
