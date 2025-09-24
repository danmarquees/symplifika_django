from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Autenticação de sessão que desabilita verificação CSRF para extensões Chrome
    """
    
    def enforce_csrf(self, request):
        """
        Desabilita verificação CSRF para requisições de extensões Chrome
        """
        # Verificar se a requisição vem de uma extensão Chrome
        origin = request.META.get('HTTP_ORIGIN', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Verificar se foi marcada pelo middleware
        if hasattr(request, '_chrome_extension') and request._chrome_extension:
            return  # Pular verificação CSRF
        
        # Se é uma extensão Chrome, pular verificação CSRF
        if (origin.startswith('chrome-extension://') or 
            'Chrome' in user_agent and 'Extension' in user_agent or
            request.path.startswith('/api/token/')):  # Endpoints de login sempre sem CSRF
            return  # Pular verificação CSRF
            
        # Para outras requisições, usar verificação normal
        return super().enforce_csrf(request)
