# -*- coding: utf-8 -*-
"""
Script para limpar sessões antigas e incorretas do banco de dados
Execute este script para limpar todas as sessões que não estão mais ativas
"""
import sys
from routes.database import execute_query, init_db

def cleanup_all_sessions():
    """Remove todas as sessões antigas do banco de dados"""
    print("🔧 Iniciando limpeza de sessões...")
    
    # Inicializa conexão
    if not init_db():
        print("❌ Erro ao conectar ao banco de dados")
        return False
    
    try:
        # Primeiro, mostra quantas sessões existem
        count_query = "SELECT COUNT(*) as total FROM active_sessions"
        result = execute_query(count_query, fetch_one=True)
        total_before = result['total'] if result else 0
        print(f"📊 Sessões antes da limpeza: {total_before}")
        
        # Mostra usuários duplicados
        duplicates_query = """
            SELECT username, COUNT(*) as count 
            FROM active_sessions 
            GROUP BY username 
            HAVING count > 1
        """
        duplicates = execute_query(duplicates_query)
        if duplicates:
            print(f"\n⚠️  Usuários com sessões duplicadas:")
            for dup in duplicates:
                print(f"   - {dup['username']}: {dup['count']} sessões")
        
        # Remove todas as sessões inativas (mais de 30 minutos sem atividade)
        cleanup_query = """
            DELETE FROM active_sessions
            WHERE TIMESTAMPDIFF(MINUTE, last_activity, NOW()) >= 30
        """
        execute_query(cleanup_query, fetch_all=False)
        
        # Conta quantas sessões restaram
        result = execute_query(count_query, fetch_one=True)
        total_after = result['total'] if result else 0
        removed = total_before - total_after
        
        print(f"\n✅ Limpeza concluída!")
        print(f"   - Sessões removidas: {removed}")
        print(f"   - Sessões restantes: {total_after}")
        
        if total_after > 0:
            # Mostra as sessões que restaram
            remaining_query = """
                SELECT username, last_activity, 
                       TIMESTAMPDIFF(MINUTE, last_activity, NOW()) as minutes_ago
                FROM active_sessions
                ORDER BY last_activity DESC
            """
            remaining = execute_query(remaining_query)
            print(f"\n📋 Sessões ativas restantes:")
            for sess in remaining:
                print(f"   - {sess['username']}: última atividade há {sess['minutes_ago']} minuto(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        return False


def cleanup_all_sessions_force():
    """Remove TODAS as sessões do banco de dados (use com cuidado!)"""
    print("⚠️  ATENÇÃO: Esta operação removerá TODAS as sessões do banco!")
    print("   Isso forçará o logout de todos os usuários ativos!")
    confirm = input("Digite 'SIM' (maiúsculo) para confirmar: ")
    
    if confirm.strip() != 'SIM':
        print("❌ Operação cancelada (é necessário digitar SIM em maiúsculas)")
        return False
    
    print("\n🔧 Removendo todas as sessões...")
    
    # Inicializa conexão
    if not init_db():
        print("❌ Erro ao conectar ao banco de dados")
        return False
    
    try:
        # Remove todas as sessões
        delete_query = "DELETE FROM active_sessions"
        execute_query(delete_query, fetch_all=False)
        
        print("✅ Todas as sessões foram removidas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao remover sessões: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("🧹 LIMPEZA DE SESSÕES - Sistema de Treinamento ADTSA")
    print("=" * 60)
    print("\nOpções:")
    print("1 - Limpar apenas sessões inativas (>30 minutos)")
    print("2 - Limpar TODAS as sessões (força logout de todos)")
    print("0 - Sair")
    print()
    
    choice = input("Escolha uma opção: ").strip()
    
    if choice == '1':
        cleanup_all_sessions()
    elif choice == '2':
        cleanup_all_sessions_force()
    elif choice == '0':
        print("👋 Saindo...")
    else:
        print("❌ Opção inválida!")
    
    print("\n" + "=" * 60)
