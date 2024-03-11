from typing import Any

from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """
    Фильтр для модели Ingredient. Позволяет фильтровать ингредиенты по имени.
    """
    name: filters.CharFilter = filters.CharFilter(lookup_expr="istartswith")

    class Meta:
        model: type[Ingredient] = Ingredient
        fields: tuple[str, ...] = ("name",)


class RecipeFilter(FilterSet):
    """
    Фильтр для модели Recipe. Позволяет фильтровать рецепты по тегам, автору,
    наличию в корзине и избранном.
    """
    tags: filters.ModelMultipleChoiceFilter = (
        filters.ModelMultipleChoiceFilter(
            field_name="tags__slug",
            to_field_name="slug",
            queryset=Tag.objects.all(),
        ))
    is_in_shopping_cart: filters.BooleanFilter = filters.BooleanFilter(
        method="filter_is_in_shopping_cart")
    is_favorited: filters.BooleanFilter = filters.BooleanFilter(
        method="filter_is_favorited")

    class Meta:
        model: type[Recipe] = Recipe
        fields: tuple[str, ...] = (
            "tags",
            "author",
            "is_in_shopping_cart",
            "is_favorited",
        )

    def filter_is_in_shopping_cart(
        self, queryset: Any, name: str, value: bool
    ) -> Any:
        """
        Фильтрует рецепты по наличию в корзине у текущего пользователя.

        :param queryset: Набор данных для фильтрации.
        :param name: Имя поля для фильтрации.
        :param value: Значение для фильтрации.
        :return: Отфильтрованный набор данных.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                recipes_shoppingcart_related__user=self.request.user)
        return queryset

    def filter_is_favorited(
        self, queryset: Any, name: str, value: bool
    ) -> Any:
        """
        Фильтрует рецепты по наличию в избранном у текущего пользователя.

        :param queryset: Набор данных для фильтрации.
        :param name: Имя поля для фильтрации.
        :param value: Значение для фильтрации.
        :return: Отфильтрованный набор данных.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                recipes_favorite_related__user=self.request.user)
        return queryset
