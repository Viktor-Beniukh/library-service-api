from django.contrib.auth import get_user_model
from django.test import TestCase

from book.models import Book
from borrowing.models import Borrowing, Payment


class ModelsTests(TestCase):

    def test_borrowing_str(self):
        book = Book.objects.create(
            title="test",
            inventory=10,
            daily_fee=5.00
        )
        borrower = get_user_model().objects.create_user(
            email="test@user.com",
            password="test12345"
        )
        borrowing = Borrowing.objects.create(
            borrow_date="2023-01-01",
            book=book,
            borrower=borrower
        )

        self.assertEqual(
            str(borrowing), f"{borrowing.id}: ('{book.title}')"
        )

    def test_payment_str(self):
        book = Book.objects.create(
            title="test",
            inventory=10,
            daily_fee=5.00
        )
        borrower = get_user_model().objects.create_user(
            email="test@user.com",
            password="test12345"
        )
        borrowing = Borrowing.objects.create(
            borrow_date="2023-01-01",
            book=book,
            borrower=borrower
        )
        payment = Payment.objects.create(
            borrowing=borrowing,
            money_to_pay=5.00
        )

        self.assertEqual(
            str(payment),
            f"Payment {payment.id} ({borrowing.book.title})"
        )
