from django.views.generic import TemplateView

class WelcomeView(TemplateView):
    template_name = "onboarding/welcome.html"

class StepsView(TemplateView):
    template_name = "onboarding/steps.html"
