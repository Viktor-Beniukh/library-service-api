from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.serializers import BookSerializer
from book.views import LibraryPagination


BOOK_URL = reverse("book:book-list")


def sample_book(**params: Any) -> Book:
    defaults = {
        "title": "Test",
        "inventory": 10,
        "daily_fee": 5.00,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id: int) -> Any:
    return reverse("book:book-detail", args=[book_id])


class UnauthenticatedBookApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_book(self) -> None:
        sample_book()
        sample_book()
        pagination = LibraryPagination

        response = self.client.get(BOOK_URL)

        book = Book.objects.all()
        serializer = BookSerializer(pagination, book, many=True)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)

    def test_retrieve_book_detail(self) -> None:
        book = sample_book()
        url = detail_url(book.id)
        pagination = LibraryPagination

        response = self.client.get(url)

        serializer = BookSerializer(pagination, book)

        if serializer.is_valid():
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, serializer.data)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com",
            "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_create_book_forbidden(self) -> None:

        payload = {
            "title": "Test",
            "inventory": 10,
            "daily_fee": 5.00,
        }

        response = self.client.post(BOOK_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "adminpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self) -> None:

        payload = {
            "title": "Test",
            "inventory": 10,
            "daily_fee": 5.00,
        }

        response = self.client.post(BOOK_URL, payload)

        book = Book.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

    def test_filter_book_by_title(self) -> None:
        sample_book(title="Book")
        sample_book(title="Sample")
        pagination = LibraryPagination

        response = self.client.get(BOOK_URL, {"title": "Book"})

        books = Book.objects.filter(title__icontains="book")
        serializer = BookSerializer(pagination, books, many=True)

        if serializer.is_valid():
            self.assertEqual(response.data, serializer.data)
