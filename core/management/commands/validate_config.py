from django.core.management.base import BaseCommand
from django.conf import settings
from core.utils import validate_api_configuration, EnvironmentHelper


class Command(BaseCommand):
    help = 'Validate API and system configuration'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Symplifika Configuration Validation ===\n')
        )

        # Validate API configuration
        config_status = validate_api_configuration()
        
        self.stdout.write('📡 API Configuration:')
        for key, status in config_status.items():
            status_icon = '✅' if status else '❌'
            self.stdout.write(f'  {status_icon} {key.replace("_", " ").title()}: {status}')
        
        self.stdout.write('\n🌐 Environment:')
        self.stdout.write(f'  📍 Environment: {"Production" if EnvironmentHelper.is_production() else "Development"}')
        self.stdout.write(f'  🔗 API Base URL: {settings.API_BASE_URL}')
        self.stdout.write(f'  🖥️  Frontend URL: {settings.FRONTEND_URL}')
        
        self.stdout.write('\n💳 Payment Configuration:')
        stripe_status = '✅ Configured' if EnvironmentHelper.is_stripe_configured() else '❌ Not configured'
        self.stdout.write(f'  💰 Stripe: {stripe_status}')
        
        self.stdout.write('\n🤖 AI Configuration:')
        ai_status = '✅ Configured' if EnvironmentHelper.is_ai_configured() else '❌ Not configured'
        self.stdout.write(f'  🧠 Gemini API: {ai_status}')
        
        # Check for common issues
        self.stdout.write('\n🔍 Potential Issues:')
        issues = []
        
        if not config_status['stripe_configured']:
            issues.append('Stripe not configured - payment features will not work')
        
        if not config_status['ai_configured']:
            issues.append('AI not configured - AI features will not work')
        
        if settings.DEBUG and 'localhost' not in settings.API_BASE_URL:
            issues.append('DEBUG=True but API_BASE_URL is not localhost')
        
        if not issues:
            self.stdout.write('  ✅ No issues found!')
        else:
            for issue in issues:
                self.stdout.write(f'  ⚠️  {issue}')
        
        self.stdout.write('\n' + '='*50)
