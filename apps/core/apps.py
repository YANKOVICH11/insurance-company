from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'   # <- ОБЯЗАТЕЛЬНО apps.core, НЕ ПРОСТО core
    verbose_name = 'Основное'