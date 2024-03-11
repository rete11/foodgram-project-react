from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class AuthorOrReadOnly(BasePermission):
    """
    Права доступа для автора или только для чтения.
    Пользователи, которые не являются авторами, могут только читать.
    Авторы могут выполнять любые операции.
    """
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Проверяет, имеет ли пользователь право на выполнение операции.

        :param request: HTTP-запрос.
        :param view: Представление, с которым связан запрос.
        :return: True, если пользователь имеет право на выполнение операции,
        иначе False.
        """
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(
        self, request: Request, view: APIView, obj: Any
    ) -> bool:
        """
        Проверяет, имеет ли пользователь право на выполнение операции
        над конкретным объектом.

        :param request: HTTP-запрос.
        :param view: Представление, с которым связан запрос.
        :param obj: Объект, над которым выполняется операция.
        :return: True, если пользователь имеет право на выполнение операции,
        иначе False.
        """
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user == obj.author
        )
