from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from book.models import Book
from book.serializers import BookSerializer


class BookPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = BookPagination
    authentication_classes = (JWTAuthentication,)
