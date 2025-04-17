from django.apps import AppConfig


class ShipopsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ShipOps'

    def ready(self):
        """
        Import templatetags to ensure they are properly registered with Django.
        """
        # Removed problematic import that contained null bytes
        pass
