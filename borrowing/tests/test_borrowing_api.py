from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.views import LibraryPagination
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)


BORROWING_URL = reverse("borrowing:borrowing-list")


def sample_borrowing(**params):
    book = Book.objects.create(
        title="test",
        inventory=10,
        daily_fee=5.00,
    )
    borrower = get_user_model().objects.create_user(
        email="test@test.com",
        password="test12345",
    )

    defaults = {
        "borrow_date": "2023-01-01",
        "book": book,
        "borrower": borrower,
    }

    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


class UnauthenticatedBorrowingApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(BORROWING_URL)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com",
            "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings(self):
        sample_borrowing()

        response = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        pagination = LibraryPagination

        serializer = BorrowingListSerializer(pagination, borrowings, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_retrieve_borrowings_detail(self):
        borrowing = sample_borrowing()
        url = detail_url(borrowing.id)
        pagination = LibraryPagination

        response = self.client.get(url)

        serializer = BorrowingDetailSerializer(pagination, borrowing)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_create_borrowing_forbidden(self):

        payload = {
            "borrow_date": "2023-01-01",
            "expected_return_date": "2023-01-04",
        }

        response = self.client.post(BORROWING_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_allow_create_borrowing_after_return_book(self):
        book = Book.objects.create(
            title="test", inventory=10, daily_fee=5.00
        )
        borrower = get_user_model().objects.create_user(
            email="test@test.com", password="test12345"
        )

        borrow_date = date.today()
        actual_return_date = date.today() + timedelta(days=5)

        payload = {
            "borrow_date": borrow_date,
            "actual_return_date": actual_return_date,
            "book": book.id,
            "borrower": borrower.id,
        }

        response = self.client.post(BORROWING_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_not_create_borrowing_if_not_return_book(self):
        book = Book.objects.create(
            title="test", inventory=10, daily_fee=5.00
        )
        borrower = get_user_model().objects.create_user(
            email="test@test.com", password="test12345"
        )

        borrow_date = date.today()

        payload = {
            "borrow_date": borrow_date,
            "actual_return_date": "",
            "book": book.id,
            "borrower": borrower.id,
        }

        response = self.client.post(BORROWING_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_borrowing_by_user_and_is_active(self):
        borrowing = sample_borrowing()
        pagination = LibraryPagination

        response = self.client.get(
            BORROWING_URL,
            {
                "user_id": borrowing.borrower.id, "is_active": True
            }
        )

        serializer = BorrowingListSerializer(pagination, borrowing)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)
