from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.views import LibraryPagination
from borrowing.models import Payment, Borrowing
from borrowing.serializers import PaymentSerializer


PAYMENT_URL = reverse("borrowing:payment-list")


def sample_payment(**params: dict) -> Payment:
    book = Book.objects.create(
        title="test", inventory=10, daily_fee=5.00,
    )
    borrower = get_user_model().objects.create_user(
        email="test@test.com", password="test12345",
    )
    borrowing = Borrowing.objects.create(
        borrow_date="2023-01-01",
        actual_return_date="2023-01-07",
        book=book,
        borrower=borrower
    )

    defaults = {
        "borrowing": borrowing,
    }

    defaults.update(params)

    return Payment.objects.create(**defaults)


def detail_url(payment_id: int):
    return reverse("borrowing:payment-detail", args=[payment_id])


class UnauthenticatedPaymentApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(PAYMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_list_payments(self) -> None:
        sample_payment()

        response = self.client.get(PAYMENT_URL)

        payments = Payment.objects.all()
        pagination = LibraryPagination

        serializer = PaymentSerializer(pagination, payments, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_retrieve_payments_detail(self) -> None:
        payment = sample_payment()
        url = detail_url(payment.id)
        pagination = LibraryPagination

        response = self.client.get(url)

        serializer = PaymentSerializer(pagination, payment)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_create_payment_forbidden(self) -> None:
        borrowing = sample_payment()

        payload = {
            "borrowing": borrowing
        }

        response = self.client.post(PAYMENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminPaymentApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_payment(self) -> None:
        borrowing = sample_payment()

        payload = {
            "borrowing": borrowing.id
        }

        response = self.client.post(PAYMENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
