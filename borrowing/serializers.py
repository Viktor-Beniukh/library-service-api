from django.conf import settings
from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing, Payment
from user.serializers import UserSerializer

from book.notifications import (
    send_new_borrowing_notification,
    send_overdue_borrowings_notification,
)


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

            send_new_borrowing_notification(borrowing_id=borrowing.id)

            return borrowing


class BorrowingUpdateSerializer(BorrowingDetailSerializer):
    borrow_date = serializers.DateField(read_only=True)
    expected_return_date = serializers.DateField(read_only=True)

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

            send_overdue_borrowings_notification()

            return instance


class PaymentSerializer(serializers.ModelSerializer):
    borrowing = serializers.PrimaryKeyRelatedField(
        queryset=Borrowing.objects.select_related("book")
    )
    money_to_pay = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "borrowing",
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

        return super(PaymentSerializer, self).create(validated_data)


class PaymentUpdateSerializer(PaymentSerializer):
    borrowing = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    session_url = serializers.URLField(read_only=True)
    session_id = serializers.CharField(read_only=True)
