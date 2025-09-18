from rest_framework.views import exception_handler
from rest_framework import status
import logging

logger = logging.getLogger("django")

def custom_exception_handler(exc, context):
    """
    Handler global para exceções do Django REST Framework.
    Retorna mensagens amigáveis e log detalhado dos erros.
    """
    response = exception_handler(exc, context)

    # Log detalhado do erro
    view = context.get('view', None)
    request = context.get('request', None)
    user = getattr(request, 'user', None)
    logger.error(
        f"API Exception: {str(exc)} | View: {view.__class__.__name__ if view else 'N/A'} | User: {user if user and user.is_authenticated else 'Anonymous'} | Path: {request.path if request else 'N/A'}",
        exc_info=True,
        extra={
            "data": getattr(request, 'data', None),
            "query_params": getattr(request, 'query_params', None),
        }
    )

    if response is not None:
        # Mensagem amigável
        default_detail = response.data.get('detail', None)
        if default_detail:
            response.data['error'] = str(default_detail)
            response.data.pop('detail', None)
        else:
            response.data['error'] = "Erro inesperado. Tente novamente mais tarde."

        # Código do erro
        response.data['code'] = getattr(exc, 'default_code', 'error')

        # Status HTTP
        response.data['status'] = response.status_code

        # Detalhes extras (se houver)
        if hasattr(exc, 'get_full_details'):
            response.data['details'] = exc.get_full_details()

    else:
        # Erro não tratado pelo DRF, retorna padrão
        return Response({
            "error": "Erro interno do servidor. Tente novamente mais tarde.",
            "code": "server_error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
