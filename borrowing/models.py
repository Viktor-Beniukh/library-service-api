from datetime import date, timedelta

from django.conf import settings
from django.db import models

from book.models import Book


def default_return_expecting_date():
    return date.today() + timedelta(days=1)


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
        return f"{self.borrow_date}"
