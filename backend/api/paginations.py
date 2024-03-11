from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Класс, представляющий пользовательскую пагинацию.
    Расширяет стандартную пагинацию PageNumberPagination из rest_framework.
    Позволяет задать размер страницы через параметр запроса "limit".
    """
    page_size_query_param: str = "limit"
