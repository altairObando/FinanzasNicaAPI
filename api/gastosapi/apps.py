from django.apps import AppConfig


class GastosapiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'gastosapi'

    def ready(self):
        import gastosapi.signals
        return super().ready()
