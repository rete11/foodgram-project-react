from django.db import transaction
from rest_framework import serializers, status
from drf_extra_fields.fields import Base64ImageField

from recipes.constants import MAX_VALUE, MIN_VALUE
from recipes.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User. Добавляет поле is_subscribed,
    которое показывает,подписан ли текущий пользователь на этого
    пользователя.
    """

    is_subscribed: serializers.SerializerMethodField = (
        serializers.SerializerMethodField(read_only=True)
    )

    class Meta:
        model: type = User
        fields: tuple = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj: User) -> bool:
        """
        Проверяет, подписан ли текущий пользователь на пользователя obj.

        :param obj: Пользователь, для которого выполняется проверка.
        :return: True, если текущий пользователь подписан на пользователя obj,
        иначе False.
        """
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and request.user.followed_users.filter(author=obj).exists()
        )


class SubscribeSerializer(UserSerializer):
    """
    Сериализатор для подписок. Наследуется от UserSerializer и добавляет поля
    recipes_count и recipes, которые показывают количество рецептов
    пользователя и сами рецепты соответственно.
    """

    recipes_count: serializers.ReadOnlyField = serializers.ReadOnlyField(
        source="recipes.count"
    )
    recipes: serializers.SerializerMethodField = (
        serializers.SerializerMethodField()
    )

    class Meta(UserSerializer.Meta):
        fields: tuple = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )
        read_only_fields: tuple = (
            "email",
            "username",
            "first_name",
            "last_name",
        )

    def get_recipes(self, obj: User) -> "RecipeShortSerializer":
        """
        Возвращает рецепты пользователя obj. Количество возвращаемых рецептов
        может быть ограничено параметром recipes_limit в запросе.

        :param obj: Пользователь, рецепты которого возвращаются.
        :return: Сериализованные рецепты пользователя obj.
        """
        queryset = obj.recipes.all()
        recipes_limit = self.context["request"].GET.get("recipes_limit")
        if recipes_limit and recipes_limit.isdigit():
            queryset = queryset[: int(recipes_limit)]
        return RecipeShortSerializer(
            queryset, many=True, context=self.context
        ).data


class SubscribeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания подписки. Проверяет, что
    пользователь не подписывается на самого себя
    и что он еще не подписан на этого пользователя.
    """

    class Meta:
        model: type = Subscription
        fields: tuple = ("user", "author")

    def validate(self, data: dict) -> dict:
        """
        Валидация данных перед созданием подписки.

        :param data: Данные для валидации.
        :return: Валидированные данные.
        """
        user_id = data.get("user").id
        author_id = data.get("author").id
        if Subscription.objects.filter(
            author=author_id, user=user_id
        ).exists():
            raise serializers.ValidationError(
                detail="Вы уже подписаны на этого пользователя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user_id == author_id:
            raise serializers.ValidationError(
                detail="Вы не можете подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def to_representation(self, instance: Subscription) -> dict:
        """
        Представление данных после создания подписки.

        :param instance: Экземпляр модели Subscription.
        :return: Представление данных.
        """
        return SubscribeSerializer(instance.author, context=self.context).data


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag.
    """

    class Meta:
        model: type = Tag
        fields: tuple = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    """

    class Meta:
        model: type = Ingredient
        fields: tuple = ("id", "name", "measurement_unit")


class AmountIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели AmountIngredient.
    """

    id: serializers.ReadOnlyField = serializers.ReadOnlyField(
        source="ingredient.id"
    )
    name: serializers.ReadOnlyField = serializers.ReadOnlyField(
        source="ingredient.name"
    )
    measurement_unit: serializers.ReadOnlyField = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model: type = AmountIngredient
        fields: tuple = ("id", "name", "measurement_unit", "amount")


class CreateAmountIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания экземпляра модели AmountIngredient.
    """

    id: serializers.PrimaryKeyRelatedField = (
        serializers.PrimaryKeyRelatedField(
            queryset=Ingredient.objects.all(),
        )
    )
    amount: serializers.IntegerField = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
        error_messages={
            "min_value": "Значение должно быть не меньше {min_value}.",
            "max_value": "Количество ингредиента не больше {max_value}",
        },
    )

    class Meta:
        fields: tuple = ("id", "amount")
        model: type = AmountIngredient


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения рецептов. Включает информацию об авторе, тегах,
    ингредиентах, а также поля, указывающие, добавлен ли рецепт в избранное
    или в корзину покупок.
    """

    image: Base64ImageField = Base64ImageField()
    author: UserSerializer = UserSerializer(read_only=True)
    tags: TagSerializer = TagSerializer(many=True, read_only=True)
    ingredients: AmountIngredientSerializer = AmountIngredientSerializer(
        many=True,
        source="recipe_ingredient",
    )
    is_favorited: serializers.SerializerMethodField = (
        serializers.SerializerMethodField()
    )
    is_in_shopping_cart: serializers.SerializerMethodField = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model: type = Recipe
        fields: tuple = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj: Recipe) -> bool:
        """
        Проверяет, добавлен ли рецепт в избранное текущим пользователем.

        :param obj: Рецепт, который проверяется.
        :return: True, если рецепт добавлен в избранное, иначе False.
        """
        return self.get_is_in_user_field(obj, "recipes_favorite_related")

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        """
        Проверяет, добавлен ли рецепт в корзину покупок текущим пользователем.

        :param obj: Рецепт, который проверяется.
        :return: True, если рецепт добавлен в корзину покупок, иначе False.
        """
        return self.get_is_in_user_field(obj, "recipes_shoppingcart_related")

    def get_is_in_user_field(self, obj: Recipe, field: str) -> bool:
        """
        Проверяет, присутствует ли рецепт в указанном поле пользователя.

        :param obj: Рецепт, который проверяется.
        :param field: Поле пользователя, в котором проверяется наличие рецепта.
        :return: True, если рецепт присутствует в указанном поле, иначе False.
        """
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and getattr(request.user, field).filter(recipe=obj).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецептов. Включает информацию об авторе,
    тегах, ингредиентах, а также валидацию данных перед созданием рецепта.
    """

    image: Base64ImageField = Base64ImageField()
    author: UserSerializer = UserSerializer(read_only=True)
    tags: serializers.PrimaryKeyRelatedField = (
        serializers.PrimaryKeyRelatedField(
            queryset=Tag.objects.all(), many=True
        )
    )
    ingredients: CreateAmountIngredientSerializer = (
        CreateAmountIngredientSerializer(many=True, write_only=True)
    )
    cooking_time: serializers.IntegerField = serializers.IntegerField(
        max_value=MAX_VALUE,
        min_value=MIN_VALUE,
        error_messages={
            "max_value": f"Количество минут не может быть больше {MAX_VALUE}",
            "min_value": f"Количество минут не может быть меньше {MIN_VALUE}",
        },
    )

    class Meta:
        model: type = Recipe
        fields: tuple = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate(self, data: dict) -> dict:
        """
        Валидация данных перед созданием рецепта.

        :param data: Данные для валидации.
        :return: Валидированные данные.
        """
        ingredients = data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Поле ингредиентов не может быть пустым!"}
            )
        if len(set(item["id"] for item in ingredients)) != len(ingredients):
            raise serializers.ValidationError(
                "Ингридиенты не должны повторяться!"
            )
        tags = data.get("tags")
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Поле тегов не может быть пустым!"}
            )
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                {"tags": "Теги не должны повторяться!"}
            )
        return data

    def validate_image(self, image: Base64ImageField) -> Base64ImageField:
        """
        Валидация изображения перед созданием рецепта.

        :param image: Изображение для валидации.
        :return: Валидированное изображение.
        """
        if not image:
            raise serializers.ValidationError(
                {"image": "Поле изображения не может быть пустым!"}
            )
        return image

    @staticmethod
    def create_ingredients(recipe: Recipe, ingredients: list) -> None:
        """
        Создает ингредиенты для рецепта.

        :param recipe: Рецепт, для которого создаются ингредиенты.
        :param ingredients: Список ингредиентов.
        """
        create_ingredients = [
            AmountIngredient(
                recipe=recipe,
                ingredient=ingredient["id"],
                amount=ingredient["amount"],
            )
            for ingredient in ingredients
        ]
        AmountIngredient.objects.bulk_create(create_ingredients)

    @transaction.atomic
    def create(self, validated_data: dict) -> Recipe:
        """
        Создает рецепт.

        :param validated_data: Проверенные данные.
        :return: Созданный рецепт.
        """
        current_user = self.context["request"].user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data, author=current_user)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """
        Обновляет рецепт.

        :param instance: Рецепт, который нужно обновить.
        :param validated_data: Проверенные данные.
        :return: Обновленный рецепт.
        """
        instance.tags.clear()
        instance.tags.set(validated_data.pop("tags"))
        instance.ingredients.clear()
        ingredients = validated_data.pop("ingredients")
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, recipe: Recipe) -> dict:
        """
        Возвращает представление рецепта.

        :param recipe: Рецепт, который нужно представить.
        :return: Представление рецепта.
        """
        return RecipeReadSerializer(recipe, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого представления рецепта.
    """

    image: Base64ImageField = Base64ImageField()

    class Meta:
        model: type = Recipe
        fields: tuple = ("id", "name", "image", "cooking_time")


class ShoppingCartCreateDeleteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и удаления товаров в корзине.
    """

    class Meta:
        model: type = ShoppingCart
        fields: tuple = ("user", "recipe")

    def validate(self, data: dict) -> dict:
        """
        Проверяет, что рецепт еще не добавлен в корзину.

        :param data: Данные для проверки.
        :return: Проверенные данные.
        """
        user_id = data.get("user").id
        recipe_id = data.get("recipe").id
        if self.Meta.model.objects.filter(
            user=user_id, recipe=recipe_id
        ).exists():
            raise serializers.ValidationError("Рецепт уже добавлен")
        return data

    def to_representation(self, instance: "ShoppingCart") -> dict:
        """
        Возвращает представление товара в корзине.

        :param instance: Товар в корзине, который нужно представить.
        :return: Представление товара в корзине.
        """
        serializer = RecipeShortSerializer(
            instance.recipe, context=self.context
        )
        return serializer.data


class FavoriteCreateDeleteSerializer(ShoppingCartCreateDeleteSerializer):
    """
    Сериализатор для создания и удаления избранных рецептов.
    """

    class Meta(ShoppingCartCreateDeleteSerializer.Meta):
        model: type = Favorite
