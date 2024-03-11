from typing import Tuple

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    """
    Административное представление для модели User.
    """
    list_display: Tuple[str, ...] = (
        "username",
        "id",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "get_recipes_count",
        "get_subscribers_count",
    )
    list_filter: Tuple[str, ...] = ("email", "first_name", "is_active")
    search_fields: Tuple[str, ...] = (
        "username",
        "email",
    )
    empty_value_display: str = "-пусто-"

    save_on_top: bool = True

    @admin.display(description="Количество рецептов")
    def get_recipes_count(self, obj: User) -> int:
        """
        Возвращает количество рецептов пользователя.

        :param obj: Объект User.
        :return: Количество рецептов.
        """
        return obj.recipes.count()

    @admin.display(description="Количество подписчиков")
    def get_subscribers_count(self, obj: User) -> int:
        """
        Возвращает количество подписчиков пользователя.

        :param obj: Объект User.
        :return: Количество подписчиков.
        """
        return obj.author.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Административное представление для модели Subscription.
    """
    list_display: Tuple[str, ...] = ("id", "user", "author")
    search_fields: Tuple[str, ...] = ("user", "author")
    list_filter: Tuple[str, ...] = ("user", "author")
    empty_value_display: str = "-пусто-"

    save_on_top: bool = True
