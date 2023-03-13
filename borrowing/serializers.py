from django.conf import settings
from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing, Payment
from user.serializers import UserSerializer

from book.notifications import send_new_borrowing_notification


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
        source="borrower.full_name", read_only=True
    )
    actual_return_date = serializers.DateField(read_only=True)

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
    actual_return_date = serializers.DateField(read_only=True)


class BorrowingCreateSerializer(BorrowingSerializer):
    actual_return_date = serializers.DateField(read_only=True)

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

            send_new_borrowing_notification(borrowing_id=borrowing.id)

            return borrowing


class BorrowingUpdateSerializer(BorrowingDetailSerializer):
    borrow_date = serializers.DateField(read_only=True)


class BorrowingReturnBookSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(
        source="book.title", read_only=True
    )
    borrower_full_name = serializers.CharField(
        source="borrower.full_name", read_only=True
    )
    actual_return_date = serializers.DateField(
        write_only=True, required=False
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book_title",
            "borrower_full_name",
            "actual_return_date"
        )


class PaymentSerializer(serializers.ModelSerializer):
    borrowing = serializers.PrimaryKeyRelatedField(
        queryset=Borrowing.objects.select_related("book", "borrower")
    )
    money_to_pay = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    book_title = serializers.CharField(
        source="borrowing.book.title", read_only=True
    )
    borrower_full_name = serializers.CharField(
        source="borrowing.borrower.full_name", read_only=True
    )
    session_url = serializers.URLField(read_only=True)
    session_id = serializers.CharField(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "borrowing",
            "book_title",
            "borrower_full_name",
            "status_payment",
            "type_payment",
            "session_url",
            "session_id",
            "money_to_pay",
        )

    def create(self, validated_data):
        borrowing = validated_data["borrowing"]
        book = borrowing.book
        days_borrowed = (
            borrowing.expected_return_date - borrowing.borrow_date
        ).days

        if days_borrowed > 0 and (
            borrowing.actual_return_date > borrowing.expected_return_date
        ):
            overdue_days = (
                borrowing.actual_return_date - borrowing.expected_return_date
            ).days
            money_to_pay = days_borrowed * book.daily_fee + (
                overdue_days * book.daily_fee * settings.FINE_MULTIPLIER
            )

            validated_data["money_to_pay"] = money_to_pay

        if days_borrowed > 0 and (
            borrowing.actual_return_date == borrowing.expected_return_date
        ):
            money_to_pay = days_borrowed * book.daily_fee

            validated_data["money_to_pay"] = money_to_pay

        if days_borrowed > 0 and (
            borrowing.actual_return_date < borrowing.expected_return_date
        ):
            days_actual = (
                borrowing.actual_return_date - borrowing.borrow_date
            ).days
            money_to_pay = days_actual * book.daily_fee

            validated_data["money_to_pay"] = money_to_pay

        return super(PaymentSerializer, self).create(validated_data)


class PaymentUpdateSerializer(PaymentSerializer):
    borrowing = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    session_url = serializers.URLField(read_only=True)
    session_id = serializers.CharField(read_only=True)
