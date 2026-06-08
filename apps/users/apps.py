from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'   # <- ОБЯЗАТЕЛЬНО apps.users, НЕ ПРОСТО users
    verbose_name = 'Пользователи'