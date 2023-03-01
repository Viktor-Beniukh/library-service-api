from rest_framework import viewsets

from book.permissions import IsAdminOrIfAllowAnyReadOnly
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "borrower")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAllowAnyReadOnly,)

    def get_serializer_class(self):

        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer

        return BorrowingSerializer
