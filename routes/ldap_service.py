"""
Serviço de autenticação LDAP/Active Directory
"""
from ldap3 import Server, Connection, ALL
import os


def authenticate_ldap(username, password):
    """
    Autentica usuário no Active Directory usando LDAP
    Retorna os dados do usuário se a autenticação for bem-sucedida, None caso contrário
    """
    try:
        # Configurações do LDAP do arquivo .env
        ldap_server = os.environ.get('LDAP_SERVER')
        ldap_domain = os.environ.get('LDAP_DOMAIN')
        ldap_search_base = os.environ.get('LDAP_SEARCH_BASE')
        
        print(f"Debug - LDAP Server: {ldap_server}")
        print(f"Debug - LDAP Domain: {ldap_domain}")
        print(f"Debug - Search Base: {ldap_search_base}")
        
        if not all([ldap_server, ldap_domain, ldap_search_base]):
            print("Erro: Variáveis de ambiente LDAP não configuradas")
            return None
        
        # Criar servidor LDAP
        print(f"Debug - Tentando conectar ao servidor: {ldap_server}")
        server = Server(ldap_server, get_info=ALL)
        
        # Tentar diferentes formatos de autenticação
        auth_successful = False
        conn = None
        
        # Método 1: UPN (User Principal Name) - username@domain.com
        try:
            user_upn = f"{username}@{ldap_domain}"
            print(f"Debug - Tentativa 1: UPN format: {user_upn}")
            conn = Connection(server, user=user_upn, password=password, auto_bind=False)
            if conn.bind():
                print("Debug - Sucesso com formato UPN!")
                auth_successful = True
        except Exception as e:
            print(f"Debug - Falha UPN: {str(e)}")
        
        # Método 2: DN completo (Distinguished Name)
        if not auth_successful:
            try:
                user_dn = f"cn={username},{ldap_search_base}"
                print(f"Debug - Tentativa 2: DN format: {user_dn}")
                conn = Connection(server, user=user_dn, password=password, auto_bind=False)
                if conn.bind():
                    print("Debug - Sucesso com formato DN!")
                    auth_successful = True
            except Exception as e:
                print(f"Debug - Falha DN: {str(e)}")
        
        # Método 3: sAMAccountName simples
        if not auth_successful:
            try:
                print(f"Debug - Tentativa 3: sAMAccountName: {username}")
                conn = Connection(server, user=username, password=password, auto_bind=False)
                if conn.bind():
                    print("Debug - Sucesso com sAMAccountName!")
                    auth_successful = True
            except Exception as e:
                print(f"Debug - Falha sAMAccountName: {str(e)}")
        
        # Se nenhum método funcionou, retornar None
        if not auth_successful:
            print("Debug - Todas as tentativas de autenticação falharam")
            return None
        
        print("Debug - Autenticação bem-sucedida, procedendo com busca de dados")
        
        # Buscar atributos do usuário
        search_filter = f"(sAMAccountName={username})"
        print(f"Debug - Buscando usuário com filtro: {search_filter}")
        
        search_result = conn.search(
            search_base=ldap_search_base,
            search_filter=search_filter,
            attributes=['displayName', 'sAMAccountName', 'mail', 'distinguishedName']
        )
        
        print(f"Debug - Resultado da busca: {search_result}, Entradas encontradas: {len(conn.entries)}")
        
        if conn.entries:
            entry = conn.entries[0]
            print(f"Debug - Usuário encontrado: {entry}")
            
            user_data = {
                'displayName': str(entry.displayName) if entry.displayName else username,
                'sAMAccountName': str(entry.sAMAccountName) if entry.sAMAccountName else username,
                'mail': str(entry.mail) if entry.mail else '',
                'distinguishedName': str(entry.distinguishedName) if entry.distinguishedName else ''
            }
            
            conn.unbind()
            return user_data
        else:
            print("Debug - Nenhuma entrada encontrada na pesquisa")
            
        conn.unbind()
        
    except Exception as e:
        print(f"Erro na autenticação LDAP: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None


def is_admin_user(user_data):
    """
    Verifica se o usuário pertence à OU 'Contas Especiais' (administrador)
    """
    if not user_data:
        return False
    
    dn = user_data.get('distinguishedName', '')
    # Verifica se o DN contém 'OU=Contas Especiais'
    return 'OU=Contas Especiais' in dn or 'ou=contas especiais' in dn.lower()
