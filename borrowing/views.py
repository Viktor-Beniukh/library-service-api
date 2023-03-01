from rest_framework import viewsets


from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "borrower")
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):

        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingSerializer
