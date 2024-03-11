from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Класс конфигурации приложения api, наследующий AppConfig.
    """
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "api"
    verbose_name: str = "api"
