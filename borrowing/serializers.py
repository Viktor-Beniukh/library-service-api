from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "borrower",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book_title = serializers.CharField(
        source="book.title", read_only=True
    )
    book_inventory = serializers.IntegerField(
        source="book.inventory", read_only=True
    )
    borrower_full_name = serializers.CharField(
        source="borrower.full_name",
        read_only=True
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_title",
            "book_inventory",
            "borrower_full_name",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)
    borrower = UserSerializer(many=False, read_only=True)


class BorrowingCreateSerializer(BorrowingSerializer):

    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        if borrowing.borrow_date:
            borrowing.book.inventory -= 1
            borrowing.book.save()
            borrowing.save()
            return borrowing
