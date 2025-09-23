from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.db import IntegrityError
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from datetime import timedelta
import time
import logging

logger = logging.getLogger(__name__)

from .models import Category, Shortcut, ShortcutUsage, AIEnhancementLog
from .serializers import (
    CategorySerializer, ShortcutSerializer, ShortcutCreateSerializer,
    ShortcutUpdateSerializer, ShortcutUsageSerializer, AIEnhancementLogSerializer,
    ShortcutSearchSerializer, ShortcutStatsSerializer, BulkShortcutActionSerializer
)
from .services import AIService


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar categorias"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).annotate(
            shortcuts_count=Count('shortcuts', filter=Q(shortcuts__is_active=True))
        ).order_by('name')

    def create(self, request, *args, **kwargs):
        """Sobrescreve create para tratar erros de integridade"""
        logger.info("CategoryViewSet.create called with data: %s", request.data)
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                logger.info("Serializer is valid, creating category")
                return super().create(request, *args, **kwargs)
            else:
                logger.warning("Serializer validation failed: %s", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.error("IntegrityError in category creation: %s", e)
            return Response(
                {'name': ['Já existe uma categoria com este nome.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Unexpected error in category creation: %s", e)
            return Response(
                {'error': 'Erro interno do servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """Sobrescreve update para tratar erros de integridade"""
        logger.info("CategoryViewSet.update called with data: %s", request.data)
        try:
            serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=kwargs.get('partial', False))
            if serializer.is_valid():
                logger.info("Serializer is valid, updating category")
                return super().update(request, *args, **kwargs)
            else:
                logger.warning("Serializer validation failed: %s", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.error("IntegrityError in category update: %s", e)
            return Response(
                {'name': ['Já existe uma categoria com este nome.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Unexpected error in category update: %s", e)
            return Response(
                {'error': 'Erro interno do servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @action(detail=True, methods=['get'])
    def shortcuts(self, request, pk=None):
        """Lista atalhos de uma categoria específica"""
        category = self.get_object()
        shortcuts = category.shortcuts.filter(is_active=True)
        serializer = ShortcutSerializer(shortcuts, many=True)
        return Response(serializer.data)


class ShortcutViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar atalhos"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Shortcut.objects.filter(user=self.request.user).order_by('-last_used', '-use_count', 'trigger')

    def get_serializer_class(self):
        if self.action == 'create':
            return ShortcutCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ShortcutUpdateSerializer
        return ShortcutSerializer

    def create(self, request, *args, **kwargs):
        """Sobrescreve create para tratar erros de integridade"""
        logger.info("ShortcutViewSet.create called with data: %s", request.data)
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                logger.info("Serializer is valid, creating shortcut")
                return super().create(request, *args, **kwargs)
            else:
                logger.warning("Serializer validation failed: %s", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.error("IntegrityError in shortcut creation: %s", e)
            return Response(
                {'trigger': ['Já existe um atalho com este gatilho.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Unexpected error in shortcut creation: %s", e)
            return Response(
                {'error': 'Erro interno do servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """Sobrescreve update para tratar erros de integridade"""
        logger.info("ShortcutViewSet.update called with data: %s", request.data)
        try:
            serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=kwargs.get('partial', False))
            if serializer.is_valid():
                logger.info("Serializer is valid, updating shortcut")
                return super().update(request, *args, **kwargs)
            else:
                logger.warning("Serializer validation failed: %s", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.error("IntegrityError in shortcut update: %s", e)
            return Response(
                {'trigger': ['Já existe um atalho com este gatilho.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Unexpected error in shortcut update: %s", e)
            return Response(
                {'error': 'Erro interno do servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def search(self, request):
        """Busca atalhos com filtros avançados"""
        serializer = ShortcutSearchSerializer(data=request.data)
        if serializer.is_valid():
            queryset = self.get_queryset()

            # Aplicar filtros
            query = serializer.validated_data.get('query')
            if query:
                queryset = queryset.filter(
                    Q(trigger__icontains=query) |
                    Q(title__icontains=query) |
                    Q(content__icontains=query)
                )

            category = serializer.validated_data.get('category')
            if category:
                queryset = queryset.filter(category_id=category)

            expansion_type = serializer.validated_data.get('expansion_type')
            if expansion_type:
                queryset = queryset.filter(expansion_type=expansion_type)

            is_active = serializer.validated_data.get('is_active')
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)

            # Ordenação
            order_by = serializer.validated_data.get('order_by', '-last_used')
            queryset = queryset.order_by(order_by)

            # Paginação
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ShortcutSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = ShortcutSerializer(queryset, many=True)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Marca um atalho como usado e retorna o conteúdo processado"""
        shortcut = self.get_object()

        # Incrementa contador de uso
        shortcut.increment_usage()

        # Registra o uso
        context = request.data.get('context', '')
        ShortcutUsage.objects.create(
            shortcut=shortcut,
            user=request.user,
            context=context
        )

        # Processa conteúdo com IA se necessário
        content = shortcut.get_processed_content()

        if (shortcut.expansion_type == 'ai_enhanced' and
            shortcut.ai_prompt and
            request.user.profile.can_use_ai()):

            content = self.enhance_with_ai(shortcut, content)

        return Response({
            'content': content,
            'use_count': shortcut.use_count,
            'last_used': shortcut.last_used
        })

    def enhance_with_ai(self, shortcut, content):
        """Expande conteúdo usando IA"""
        try:
            start_time = time.time()
            ai_service = AIService()

            enhanced_content = ai_service.enhance_text(
                content,
                shortcut.ai_prompt
            )

            processing_time = time.time() - start_time

            # Salva o log apenas se houve expansão real
            if enhanced_content != content:
                AIEnhancementLog.objects.create(
                    shortcut=shortcut,
                    original_content=content,
                    enhanced_content=enhanced_content,
                    ai_model_used=ai_service.model_name,
                    processing_time=processing_time
                )

                # Atualiza contador de uso de IA
                self.request.user.profile.increment_ai_usage()

                # Salva conteúdo expandido no atalho
                shortcut.expanded_content = enhanced_content
                shortcut.save(update_fields=['expanded_content'])

            return enhanced_content

        except Exception as e:
            logger.error(f"Erro no enhance_with_ai: {e}")
            # Em caso de erro, retorna conteúdo original
            return content

    @action(detail=True, methods=['post'])
    def regenerate_ai(self, request, pk=None):
        """Regenera conteúdo expandido pela IA"""
        shortcut = self.get_object()

        if not request.user.profile.can_use_ai():
            return Response(
                {'error': 'Limite de uso de IA atingido'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        if shortcut.expansion_type != 'ai_enhanced':
            return Response(
                {'error': 'Este atalho não usa expansão por IA'},
                status=status.HTTP_400_BAD_REQUEST
            )

        enhanced_content = self.enhance_with_ai(shortcut, shortcut.content)

        return Response({
            'enhanced_content': enhanced_content,
            'ai_requests_remaining': (
                shortcut.user.profile.max_ai_requests -
                shortcut.user.profile.ai_requests_used
            )
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estatísticas dos atalhos do usuário"""
        queryset = self.get_queryset()

        total_shortcuts = queryset.count()
        active_shortcuts = queryset.filter(is_active=True).count()
        total_uses = queryset.aggregate(total=Sum('use_count'))['total'] or 0

        # Atalho mais usado
        most_used = queryset.filter(use_count__gt=0).order_by('-use_count').first()

        # Atalhos recentes (últimos 5)
        recent_shortcuts = queryset.order_by('-created_at')[:5]

        # Estatísticas por categoria
        shortcuts_by_category = dict(
            queryset.values('category__name')
            .annotate(count=Count('id'))
            .values_list('category__name', 'count')
        )

        # Estatísticas por tipo
        shortcuts_by_type = dict(
            queryset.values('expansion_type')
            .annotate(count=Count('id'))
            .values_list('expansion_type', 'count')
        )

        stats_data = {
            'total_shortcuts': total_shortcuts,
            'active_shortcuts': active_shortcuts,
            'total_uses': total_uses,
            'most_used_shortcut': most_used,
            'recent_shortcuts': recent_shortcuts,
            'shortcuts_by_category': shortcuts_by_category,
            'shortcuts_by_type': shortcuts_by_type
        }

        serializer = ShortcutStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Executa ações em lote nos atalhos"""
        serializer = BulkShortcutActionSerializer(data=request.data)
        if serializer.is_valid():
            shortcut_ids = serializer.validated_data['shortcut_ids']
            action_type = serializer.validated_data['action']

            # Filtra apenas atalhos do usuário
            shortcuts = self.get_queryset().filter(id__in=shortcut_ids)

            if action_type == 'activate':
                shortcuts.update(is_active=True)
            elif action_type == 'deactivate':
                shortcuts.update(is_active=False)
            elif action_type == 'delete':
                shortcuts.delete()
            elif action_type == 'change_category':
                category_id = serializer.validated_data.get('category_id')
                category = get_object_or_404(Category, id=category_id, user=request.user)
                shortcuts.update(category=category)

            return Response({'message': f'Ação {action_type} executada em {shortcuts.count()} atalhos'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def most_used(self, request):
        """Retorna os atalhos mais usados"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        queryset = self.get_queryset().filter(
            last_used__gte=start_date
        ).order_by('-use_count')[:10]

        serializer = ShortcutSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def usage_history(self, request, pk=None):
        """Retorna histórico de uso de um atalho"""
        shortcut = self.get_object()
        usage_history = shortcut.usage_history.all()[:50]  # Últimos 50 usos

        serializer = ShortcutUsageSerializer(usage_history, many=True)
        return Response(serializer.data)


class ShortcutUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualizar histórico de uso"""
    serializer_class = ShortcutUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return ShortcutUsage.objects.filter(user=self.request.user).order_by('-used_at')


class AIEnhancementLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualizar logs de expansão por IA"""
    serializer_class = AIEnhancementLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return AIEnhancementLog.objects.filter(shortcut__user=self.request.user).order_by('-created_at')
