# -*- coding: utf-8 -*-
"""
Script para verificar o estado atual das sessões no banco de dados
"""
from routes.database import execute_query, init_db

def check_sessions():
    """Verifica e exibe o estado atual das sessões"""
    print("=" * 70)
    print("🔍 VERIFICAÇÃO DE SESSÕES - Sistema de Treinamento ADTSA")
    print("=" * 70)
    
    # Inicializa conexão
    if not init_db():
        print("❌ Erro ao conectar ao banco de dados")
        return False
    
    try:
        # 1. Total de sessões
        count_query = "SELECT COUNT(*) as total FROM active_sessions"
        result = execute_query(count_query, fetch_one=True)
        total_sessions = result['total'] if result else 0
        
        print(f"\n📊 ESTATÍSTICAS GERAIS")
        print(f"   Total de sessões registradas: {total_sessions}")
        
        if total_sessions == 0:
            print("\n✅ Nenhuma sessão ativa no momento")
            print("   (Isso é esperado após limpeza ou se ninguém estiver logado)")
            return True
        
        # 2. Sessões ativas (< 30 minutos)
        active_query = """
            SELECT COUNT(*) as total 
            FROM active_sessions 
            WHERE TIMESTAMPDIFF(MINUTE, last_activity, NOW()) < 30
        """
        result = execute_query(active_query, fetch_one=True)
        active_sessions = result['total'] if result else 0
        print(f"   Sessões ativas (< 30min): {active_sessions}")
        
        # 3. Sessões inativas (> 30 minutos)
        inactive_count = total_sessions - active_sessions
        print(f"   Sessões inativas (> 30min): {inactive_count}")
        
        # 4. Verificar duplicações
        duplicates_query = """
            SELECT username, COUNT(*) as count 
            FROM active_sessions 
            GROUP BY username 
            HAVING count > 1
        """
        duplicates = execute_query(duplicates_query)
        
        if duplicates:
            print(f"\n⚠️  USUÁRIOS COM MÚLTIPLAS SESSÕES (DUPLICAÇÕES):")
            for dup in duplicates:
                print(f"   ❌ {dup['username']}: {dup['count']} sessões")
        else:
            print(f"\n✅ Nenhuma duplicação encontrada!")
        
        # 5. Listar todas as sessões
        if total_sessions > 0 and total_sessions <= 20:
            print(f"\n📋 DETALHES DAS SESSÕES:")
            details_query = """
                SELECT 
                    username,
                    login_time,
                    last_activity,
                    TIMESTAMPDIFF(MINUTE, last_activity, NOW()) as minutos_inativo,
                    ip_address,
                    LEFT(session_id, 8) as session_preview
                FROM active_sessions
                ORDER BY last_activity DESC
            """
            sessions = execute_query(details_query)
            
            for sess in sessions:
                status = "🟢 ATIVO" if sess['minutos_inativo'] < 30 else "🔴 INATIVO"
                print(f"\n   {status}")
                print(f"   Usuário: {sess['username']}")
                print(f"   Login: {sess['login_time']}")
                print(f"   Última atividade: {sess['last_activity']} (há {sess['minutos_inativo']} min)")
                print(f"   IP: {sess['ip_address']}")
                print(f"   Session ID: {sess['session_preview']}...")
        
        # 6. Sessões por status
        print(f"\n📈 DISTRIBUIÇÃO POR TEMPO DE INATIVIDADE:")
        distribution_query = """
            SELECT 
                CASE 
                    WHEN TIMESTAMPDIFF(MINUTE, last_activity, NOW()) < 5 THEN '< 5 min'
                    WHEN TIMESTAMPDIFF(MINUTE, last_activity, NOW()) < 15 THEN '5-15 min'
                    WHEN TIMESTAMPDIFF(MINUTE, last_activity, NOW()) < 30 THEN '15-30 min'
                    ELSE '> 30 min'
                END as faixa,
                COUNT(*) as count
            FROM active_sessions
            GROUP BY faixa
            ORDER BY 
                CASE faixa
                    WHEN '< 5 min' THEN 1
                    WHEN '5-15 min' THEN 2
                    WHEN '15-30 min' THEN 3
                    ELSE 4
                END
        """
        distribution = execute_query(distribution_query)
        for dist in distribution:
            print(f"   {dist['faixa']}: {dist['count']} sessões")
        
        # 7. Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        if inactive_count > 0:
            print(f"   ⚠️  Há {inactive_count} sessão(ões) inativa(s) que pode(m) ser limpa(s)")
            print(f"   Execute: python cleanup_sessions.py")
        
        if duplicates:
            print(f"   ❌ ATENÇÃO: Duplicações detectadas!")
            print(f"   Execute limpeza imediatamente: python cleanup_sessions.py")
        
        if active_sessions == 0 and total_sessions > 0:
            print(f"   ℹ️  Todas as sessões estão inativas")
            print(f"   Recomenda-se executar limpeza")
        
        if active_sessions > 0 and not duplicates:
            print(f"   ✅ Sistema funcionando normalmente!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante verificação: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    check_sessions()
    print("\n" + "=" * 70)
