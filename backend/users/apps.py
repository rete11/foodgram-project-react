from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Класс конфигурации приложения users, наследующий AppConfig.
    """
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "users"
    verbose_name: str = "пользователи"
