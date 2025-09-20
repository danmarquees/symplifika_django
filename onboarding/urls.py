from django.urls import path
from . import views

app_name = 'onboarding'

urlpatterns = [
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
    path('steps/', views.StepsView.as_view(), name='steps'),
]
