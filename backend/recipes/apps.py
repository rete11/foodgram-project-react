from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """
    Конфигурация приложения "рецепты".
    """
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "recipes"
    verbose_name: str = "рецепты"
