from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import LoginSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_token_obtain_pair(request):
    """
    Custom token obtain pair view que permite login com email ou username
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Atualizar last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_premium': hasattr(user, 'profile') and user.profile.plan in ['premium', 'enterprise']
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Credenciais inválidas',
        'details': serializer.errors
    }, status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def flexible_login(request):
    """
    Endpoint de login flexível que aceita 'email', 'username' ou 'login' como campo de identificação
    """
    import logging
    import json
    logger = logging.getLogger(__name__)
    
    try:
        # Tentar extrair dados de diferentes formas
        data = {}
        
        # Primeiro tentar request.data (DRF)
        if hasattr(request, 'data') and request.data:
            data = request.data
            logger.info(f"Using request.data: {data}")
        # Se não funcionar, tentar request.POST
        elif request.POST:
            data = request.POST
            logger.info(f"Using request.POST: {data}")
        # Se não funcionar, tentar request.body (JSON raw)
        elif request.body:
            try:
                data = json.loads(request.body.decode('utf-8'))
                logger.info(f"Using request.body JSON: {data}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                data = {}
        
        logger.info(f"Login attempt - Content type: {request.content_type}")
        logger.info(f"Login attempt - Method: {request.method}")
        logger.info(f"Login attempt - Headers: {dict(request.headers)}")
        
        # Extrair dados do request com múltiplas tentativas
        login_field = (
            data.get('email') or 
            data.get('username') or 
            data.get('login') or
            request.POST.get('email') or
            request.POST.get('username') or
            request.POST.get('login')
        )
        
        password = (
            data.get('password') or
            request.POST.get('password')
        )
        
        logger.info(f"Extracted - login_field: {login_field}, password_provided: {bool(password)}")
        
        if not login_field or not password:
            logger.warning(f"Missing credentials - login_field: '{login_field}', password: {bool(password)}")
            return Response({
                'error': 'Email/username e senha são obrigatórios',
                'debug_info': {
                    'login_field': login_field,
                    'password_provided': bool(password),
                    'request_data': data,
                    'request_post': dict(request.POST),
                    'content_type': request.content_type,
                    'method': request.method,
                    'body_preview': request.body.decode('utf-8')[:100] if request.body else 'No body'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return Response({
            'error': 'Erro interno no processamento da requisição',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Preparar dados para o serializer
    serializer_data = {
        'username': login_field,  # O LoginSerializer trata isso internamente
        'password': password
    }
    
    logger.info(f"Serializer data: {serializer_data}")
    serializer = LoginSerializer(data=serializer_data, context={'request': request})
    
    if serializer.is_valid():
        logger.info("Serializer validation successful")
        user = serializer.validated_data['user']
        logger.info(f"User authenticated: {user.username}")
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Atualizar last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        logger.info("Login successful, tokens generated")
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_premium': hasattr(user, 'profile') and user.profile.plan in ['premium', 'enterprise']
            }
        }, status=status.HTTP_200_OK)
    
    logger.warning(f"Serializer validation failed: {serializer.errors}")
    return Response({
        'error': 'Credenciais inválidas',
        'details': serializer.errors,
        'serializer_data_sent': serializer_data
    }, status=status.HTTP_401_UNAUTHORIZED)
