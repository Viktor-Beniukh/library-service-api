from datetime import date, timedelta

from django.conf import settings
from django.db import models

from book.models import Book


def default_return_expecting_date():
    return date.today() + timedelta(days=3)


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField(
        default=default_return_expecting_date()
    )
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    class Meta:
        ordering = ("borrow_date",)

    def __str__(self):
        return f"{self.id}: ('{self.book.title}')"


class Payment(models.Model):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    PAYMENT = "PAYMENT"
    FINE = "FINE"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PAID, "Paid"),
        (CANCELLED, "Cancelled")
    ]
    TYPE_CHOICES = [
        (PAYMENT, "Payment"),
        (FINE, "Fine")
    ]

    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    status_payment = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PENDING
    )
    type_payment = models.CharField(
        max_length=7, choices=TYPE_CHOICES, default=PAYMENT
    )
    session_url = models.URLField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    money_to_pay = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    def __str__(self):
        return f"Payment {self.id} ({self.borrowing.book.title})"
