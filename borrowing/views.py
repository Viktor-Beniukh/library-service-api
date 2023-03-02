from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingUpdateSerializer,
)


class LibraryPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "borrower")
    serializer_class = BorrowingSerializer
    pagination_class = LibraryPagination

    def get_serializer_class(self):

        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "update":
            return BorrowingUpdateSerializer

        return BorrowingSerializer
