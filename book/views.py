from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from book.models import Book
from book.permissions import IsAdminOrIfAllowAnyReadOnly
from book.serializers import BookSerializer


class LibraryPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = LibraryPagination
    permission_classes = (IsAdminOrIfAllowAnyReadOnly,)
