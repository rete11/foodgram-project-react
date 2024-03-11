from typing import Type, Union

from django.db.models import QuerySet, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import CustomPagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (FavoriteCreateDeleteSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer,
                             ShoppingCartCreateDeleteSerializer,
                             SubscribeCreateSerializer, SubscribeSerializer,
                             TagSerializer)
from recipes.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class MyUserViewSet(UserViewSet):
    """
    Представление для модели User. Позволяет просматривать, создавать,
    обновлять и удалять пользователей.
    """

    queryset: QuerySet[User] = User.objects.all()
    permission_classes: tuple = (AllowAny,)
    pagination_class: type = CustomPagination

    def get_permissions(self) -> list:
        """
        Возвращает разрешения для текущего действия.

        :return: Список разрешений.
        """
        if self.action in ["retrieve", "list"]:
            return [AllowAny()]
        elif self.action == "me":
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id=None) -> Response:
        """
        Подписывает текущего пользователя на пользователя с указанным id.

        :param request: HTTP-запрос.
        :param id: ID пользователя, на которого подписывается текущий
        пользователь.
        :return: Ответ HTTP.
        """
        if not User.objects.filter(id=id).exists():
            return Response(
                {"error": "Автор не найден!"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = SubscribeCreateSerializer(
            data={"user": request.user.id, "author": id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None) -> Response:
        """
        Отписывает текущего пользователя от пользователя с указанным id.

        :param request: HTTP-запрос.
        :param id: ID пользователя, от которого отписывается текущий
        пользователь.
        :return: Ответ HTTP.
        """
        if not User.objects.filter(id=id).exists():
            return Response(
                {"error": "Автор не найден!"},
                status=status.HTTP_404_NOT_FOUND,)
        subscription = Subscription.objects.filter(
            user=request.user, author=id)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Вы не подписаны на этого пользователя"},
            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request) -> Response:
        """
        Возвращает подписки текущего пользователя.

        :param request: HTTP-запрос.
        :return: Ответ HTTP.
        """
        subscriptions = User.objects.filter(author__user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = SubscribeSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для модели Ingredient. Позволяет просматривать ингредиенты.
    """

    queryset: QuerySet[Ingredient] = Ingredient.objects.all()
    serializer_class: type = IngredientSerializer
    filter_backends: list = [DjangoFilterBackend]
    filterset_class: type = IngredientFilter
    pagination_class: type = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для модели Tag. Позволяет просматривать теги.
    """

    queryset: QuerySet[Tag] = Tag.objects.all()
    serializer_class: type = TagSerializer
    pagination_class: type = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Представление для модели Recipe. Позволяет просматривать,
    создавать, обновлять и удалять рецепты.
    """

    queryset: QuerySet[Recipe] = Recipe.objects.select_related(
        "author"
    ).prefetch_related("tags", "ingredients")
    permission_classes: list = [AuthorOrReadOnly]
    pagination_class: type = CustomPagination
    filter_backends: list = [DjangoFilterBackend]
    filterset_class: type = RecipeFilter

    def get_serializer_class(
        self,
    ) -> Union[Type[RecipeReadSerializer], Type[RecipeCreateSerializer]]:
        """
        Возвращает класс сериализатора в зависимости от метода HTTP-запроса.

        :return: Класс сериализатора.
        """
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @staticmethod
    def create_favorite_or_shoppingcart(
        serializer_class: Type[
            Union[
                FavoriteCreateDeleteSerializer,
                ShoppingCartCreateDeleteSerializer,
            ]
        ],
        id: int,
        request: Request,
    ) -> Response:
        """
        Создает избранный рецепт или добавляет рецепт в корзину покупок.

        :param serializer_class: Класс сериализатора.
        :param id: ID рецепта.
        :param request: HTTP-запрос.
        :return: Ответ HTTP.
        """
        serializer = serializer_class(
            data={"user": request.user.id, "recipe": id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_favorite_or_shoppingcart(
        model: Type[Union[Favorite, ShoppingCart]],
        id: int,
        request: Request,
    ) -> Response:
        """
        Удаляет избранный рецепт или удаляет рецепт из корзины покупок.

        :param model: Модель данных.
        :param id: ID рецепта.
        :param request: HTTP-запрос.
        :return: Ответ HTTP.
        """
        object = model.objects.filter(user=request.user, recipe_id=id)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Этого рецепта нет в списке"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request: Request, pk=None) -> Response:
        """
        Добавляет рецепт в избранное.

        :param request: HTTP-запрос.
        :param pk: ID рецепта.
        :return: Ответ HTTP.
        """
        return self.create_favorite_or_shoppingcart(
            FavoriteCreateDeleteSerializer, pk, request
        )

    @favorite.mapping.delete
    def del_favorite(self, request: Request, pk=None) -> Response:
        """
        Удаляет рецепт из избранного.

        :param request: HTTP-запрос.
        :param pk: ID рецепта.
        :return: Ответ HTTP.
        """
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {"error": "Рецепт не найден!"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return self.delete_favorite_or_shoppingcart(Favorite, pk, request)

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request: Request, pk=None) -> Response:
        """
        Добавляет рецепт в корзину покупок.

        :param request: HTTP-запрос.
        :param pk: ID рецепта.
        :return: Ответ HTTP.
        """
        return self.create_favorite_or_shoppingcart(
            ShoppingCartCreateDeleteSerializer, pk, request
        )

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request: Request, pk=None) -> Response:
        """
        Удаляет рецепт из корзины покупок.

        :param request: HTTP-запрос.
        :param pk: ID рецепта.
        :return: Ответ HTTP.
        """
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {"error": "Рецепт не найден!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return self.delete_favorite_or_shoppingcart(ShoppingCart, pk, request)

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request: Request) -> Response:
        """
        Загружает список покупок.

        :param request: HTTP-запрос.
        :return: Ответ HTTP.
        """
        shopping_cart = (
            AmountIngredient.objects.select_related("recipe", "ingredient")
            .filter(recipe__recipes_shoppingcart_related__user=request.user)
            .values_list(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        return self.create_file_response(shopping_cart)

    @staticmethod
    def create_file_response(
        shopping_cart: QuerySet[AmountIngredient],
    ) -> HttpResponse:
        """
        Создает файл с содержимым корзины покупок.

        :param shopping_cart: Корзина покупок.
        :return: Ответ HTTP.
        """
        content = "\n".join(
            "\t".join(map(str, item)) for item in shopping_cart
        )
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="list.txt"'
        return response
