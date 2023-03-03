from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing, Payment
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

        if borrowing.book.inventory == 0:
            raise serializers.ValidationError(
                "I’m sorry, but there are no more books"
            )

        if borrowing.borrow_date:
            borrowing.book.inventory -= 1
            borrowing.book.save()
            borrowing.save()

            return borrowing


class BorrowingUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("actual_return_date",)

    def update(self, instance, validated_data):

        if instance.actual_return_date is not None:
            raise serializers.ValidationError(
                "This book has already been returned"
            )

        instance.actual_return_date = validated_data.get(
            "actual_return_date", instance.actual_return_date
        )

        if instance.actual_return_date:
            instance.book.inventory += 1
            instance.book.save()
            instance.save()

            return instance


class PaymentSerializer(serializers.ModelSerializer):
    borrowing = serializers.PrimaryKeyRelatedField(
        queryset=Borrowing.objects.all()
    )
    money_to_pay = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "borrowing",
            "status",
            "type",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ("status", "type")
