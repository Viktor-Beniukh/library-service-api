from rest_framework import viewsets

from book.permissions import IsAdminOrIfAuthenticatedReadOnly
from book.views import LibraryPagination

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingUpdateSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "borrower")
    serializer_class = BorrowingSerializer
    pagination_class = LibraryPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        status = self.request.user.is_staff
        user_id_str = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        queryset = self.queryset

        if user_id_str:
            queryset = queryset.filter(borrower_id=int(user_id_str))

        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)

        if status is False:
            queryset = queryset.filter(borrower=self.request.user)

        return queryset

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
