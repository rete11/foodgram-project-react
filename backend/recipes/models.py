from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Length

from recipes.constants import (AMOUNT_ING, AMOUNT_ING_UNIT, AUTHOR_HELP_TEXT,
                               COLOR_HELP_TEXT, IMAGE_HELP_TEXT, ING_HELP_TEXT,
                               ING_USE, MAX_HEX, MAX_LEN_TITLE, MAX_VALUE,
                               MIN_VALUE, RECIPE_HELP_TEXT, RECIPE_ING,
                               RECIPE_TAGS, SLUG_HELP_TEXT, TAG_HELP_TEXT,
                               TEXT_HELP_TEXT, TIME_HELP_TEXT, UNIT_HELP_TEXT)
from users.models import User

models.CharField.register_lookup(Length)


class Ingredient(models.Model):
    """
    Модель для ингредиентов.
    """

    name: str = models.CharField(
        verbose_name="Название",
        max_length=MAX_LEN_TITLE,
        help_text=ING_HELP_TEXT,
    )
    measurement_unit: str = models.CharField(
        verbose_name="Единица измерения",
        max_length=MAX_LEN_TITLE,
        help_text=UNIT_HELP_TEXT,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_unit",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    """
    Модель для тегов.
    """

    name: str = models.CharField(
        verbose_name="Название тега",
        unique=True,
        max_length=MAX_LEN_TITLE,
        help_text=TAG_HELP_TEXT,
    )
    color: str = ColorField(
        verbose_name="HEX-код",
        max_length=MAX_HEX,
        unique=True,
        help_text=COLOR_HELP_TEXT,
    )
    slug: str = models.SlugField(
        verbose_name="Слаг",
        unique=True,
        max_length=MAX_LEN_TITLE,
        help_text=SLUG_HELP_TEXT,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """
    Модель для рецептов.
    """

    name: str = models.CharField(
        verbose_name="Название рецепта",
        max_length=MAX_LEN_TITLE,
        help_text=RECIPE_HELP_TEXT,
    )
    image: models.ImageField = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/images/",
        help_text=IMAGE_HELP_TEXT,
    )
    text: str = models.TextField(
        verbose_name="Описание", help_text=TEXT_HELP_TEXT
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
        help_text=AUTHOR_HELP_TEXT,
    )
    pub_date: models.DateTimeField = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )
    cooking_time: models.PositiveSmallIntegerField = (
        models.PositiveSmallIntegerField(
            "Время приготовления",
            validators=[
                MinValueValidator(
                    MIN_VALUE, message=f"Минимум {MIN_VALUE} минута!"
                ),
                MaxValueValidator(
                    MAX_VALUE, message=f"Максимум {MAX_VALUE} минут!"
                ),
            ],
            help_text=TIME_HELP_TEXT,
        )
    )
    tags: models.ManyToManyField = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        related_name="recipes",
        blank=True,
        help_text=RECIPE_TAGS,
    )
    ingredients: models.ManyToManyField = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингридиенты",
        related_name="recipes",
        through="AmountIngredient",
        help_text=RECIPE_ING,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)
        constraints = (
            models.CheckConstraint(
                check=models.Q(name__length__gt=0),
                name="\n%(app_label)s_%(class)s_name is empty\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.name}. Автор: {self.author.username}"


class AmountIngredient(models.Model):
    """
    Модель для количества ингредиентов в рецепте.
    """

    recipe: models.ForeignKey = models.ForeignKey(
        Recipe,
        related_name="recipe_ingredient",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text=AMOUNT_ING,
    )
    ingredient: models.ForeignKey = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        help_text=ING_USE,
    )
    amount: models.PositiveSmallIntegerField = (
        models.PositiveSmallIntegerField(
            verbose_name="Количество",
            help_text=AMOUNT_ING_UNIT,
            validators=(
                MinValueValidator(
                    MIN_VALUE, message=f"Должно быть {MIN_VALUE} и больше"
                ),
                MaxValueValidator(
                    MAX_VALUE,
                    message=(
                        "Число должно быть меньше чем {settings.MAX_VALUE}"
                    ),
                ),
            ),
        )
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты рецепта"
        ordering = ("recipe",)

    def __str__(self) -> str:
        """
        Возвращает строковое представление количества ингредиента в рецепте.
        """
        return (
            f"{self.ingredient.name} ({self.ingredient.measurement_unit}) - "
            f"{self.amount} "
        )


class UserRecipeRelation(models.Model):
    """
    Абстрактная модель для отношений между пользователем и рецептом.
    """

    user: models.ForeignKey = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
    )
    recipe: models.ForeignKey = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name=(
                    "\n%(app_label)s_%(class)s recipe is"
                    " already related to user\n"
                ),
            ),
        )


class Favorite(UserRecipeRelation):
    """
    Модель для избранных рецептов пользователя.
    """

    date_added: models.DateTimeField = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
        editable=False,
    )

    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self) -> str:
        """
        Возвращает строковое представление избранного рецепта пользователя.
        """
        return f"{self.user} добавил '{self.recipe}' в Избранное"


class ShoppingCart(UserRecipeRelation):
    """
    Модель для рецептов в корзине пользователя.
    """

    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"

    def __str__(self) -> str:
        """
        Возвращает строковое представление рецепта в корзине пользователя.
        """
        return f"{self.recipe} в корзине у {self.user}"
