from typing import Tuple, Type

from django.contrib import admin
from django.utils.safestring import mark_safe

from .constants import MAX_VALUE, MIN_VALUE
from .models import (AmountIngredient, Favorite, Ingredient, Recipe,
                     ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    """
    Встроенное представление для модели AmountIngredient
    в административной панели.
    """

    model: Type[AmountIngredient] = AmountIngredient
    extra: int = 1
    min_num: int = MIN_VALUE
    max_num: int = MAX_VALUE
    validate_min: bool = True
    validate_max: bool = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Представление для модели Recipe в административной панели.
    """

    list_display: Tuple[str, ...] = (
        "name",
        "author",
        "get_image",
        "cooking_time",
        "count_favorites",
        "get_ingredients",
    )
    fields: Tuple[Tuple[str, ...], ...] = (
        (
            "name",
            "cooking_time",
        ),
        (
            "author",
            "tags",
        ),
        ("text",),
        ("image",),
    )
    raw_id_fields: Tuple[str, ...] = ("author",)
    search_fields: Tuple[str, ...] = (
        "name",
        "author__username",
        "tags__name",
    )
    list_filter: Tuple[str, ...] = ("name", "author__username", "tags__name")

    inlines: Tuple[Type[IngredientInline], ...] = (IngredientInline,)
    save_on_top: bool = True
    empty_value_display: str = "-пусто-"

    @admin.display(description="Фотография")
    def get_image(self, obj: Recipe) -> str:
        """
        Возвращает HTML-код изображения рецепта.

        :param obj: Объект Recipe.
        :return: HTML-код изображения.
        """
        return mark_safe(f"<img src={obj.image.url} width='80' hieght='30'")

    @admin.display(description="В избранном")
    def count_favorites(self, obj: Recipe) -> int:
        """
        Возвращает количество пользователей, добавивших рецепт в избранное.

        :param obj: Объект Recipe.
        :return: Количество пользователей, добавивших рецепт в избранное.
        """
        return obj.recipes_favorite_related.count()

    @admin.display(description="Ингредиенты")
    def get_ingredients(self, obj: Recipe) -> str:
        """
        Возвращает список ингредиентов рецепта.

        :param obj: Объект Recipe.
        :return: Список ингредиентов.
        """
        return ", ".join(
            ingredient.name for ingredient in obj.ingredients.all()
        )

    list_display_links: Tuple[str, ...] = ("name", "author")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Представление для модели Ingredient в административной панели.
    """

    list_display: Tuple[str, ...] = (
        "name",
        "measurement_unit",
    )
    search_fields: Tuple[str, ...] = ("name",)
    list_filter: Tuple[str, ...] = ("name",)
    empty_value_display: str = "-пусто-"

    save_on_top: bool = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Представление для модели Tag в административной панели.
    """

    list_display: Tuple[str, ...] = (
        "name",
        "color",
        "slug",
    )
    empty_value_display: str = "-пусто-"
    search_fields: Tuple[str, ...] = ("name", "color")
    list_display_links: Tuple[str, ...] = ("name", "color")
    save_on_top: bool = True


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Представление для модели ShoppingCart в административной панели.
    """

    list_display: Tuple[str, ...] = (
        "user",
        "recipe",
    )
    search_fields: Tuple[str, ...] = ("user__username", "recipe__name")
    empty_value_display: str = "-пусто-"
    list_display_links: Tuple[str, ...] = ("user", "recipe")
    save_on_top: bool = True


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Представление для модели Favorite в административной панели.
    """

    list_display: Tuple[str, ...] = (
        "user",
        "recipe",
        "date_added",
    )
    search_fields: Tuple[str, ...] = ("user__username", "recipe__name")
    empty_value_display: str = "-пусто-"
    list_display_links: Tuple[str, ...] = ("user", "recipe")
    save_on_top: bool = True


@admin.register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    """
    Представление для модели AmountIngredient в административной панели.
    """

    list_display: Tuple[str, ...] = (
        "recipe",
        "ingredient",
        "amount",
    )
    empty_value_display: str = "-пусто-"
    list_display_links: Tuple[str, ...] = ("recipe", "ingredient")
    save_on_top: bool = True
