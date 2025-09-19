from django.views.generic import ListView
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from .api import NotificationListAPI

# Caso não exista um modelo Notification, você pode criar um mock ou ajustar conforme necessário.
# Aqui está um exemplo básico usando um dicionário estático.
# Em produção, substitua por um modelo real, ex: from .models import Notification

class NotificationListView(ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        # Exemplo estático, substitua por: Notification.objects.filter(user=self.request.user)
        return [
            {"title": "Bem-vindo!", "message": "Sua conta foi criada com sucesso."},
            {"title": "Atualização", "message": "Seu perfil foi atualizado."},
        ]

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class NotificationSettingsView(TemplateView):
    template_name = "notifications/settings.html"
