from django.apps import AppConfig

class BkcoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'esb.bkcore'

    #def ready(self):
    #    from .models import register_models
    #    register_models()
