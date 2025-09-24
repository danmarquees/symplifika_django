from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class ChromeExtensionMiddleware(MiddlewareMixin):
    """
    Middleware para lidar com requisições de extensões Chrome
    """
    
    def process_request(self, request):
        """
        Processa requisições antes das views
        """
        # Verificar se a requisição vem de uma extensão Chrome
        origin = request.META.get('HTTP_ORIGIN', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Se é uma extensão Chrome, marcar para pular CSRF
        if origin.startswith('chrome-extension://'):
            # Marcar a requisição como vinda de extensão Chrome
            request._chrome_extension = True
            
            # Adicionar headers CORS necessários
            request._cors_headers = {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Accept, Content-Type, Authorization, X-Requested-With',
            }
        
        return None
    
    def process_response(self, request, response):
        """
        Processa respostas após as views
        """
        # Se a requisição foi marcada como extensão Chrome, adicionar headers CORS
        if hasattr(request, '_cors_headers'):
            for header, value in request._cors_headers.items():
                response[header] = value
        
        return response
