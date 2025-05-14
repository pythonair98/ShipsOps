from django.apps import AppConfig


class ShipsauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ShipsAuth'
    
    def ready(self):
        import ShipsAuth.signals  # Import signals when app is ready
