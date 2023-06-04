from django.test import TestCase

from book.models import Book


class ModelsTests(TestCase):

    def test_book_str(self) -> None:
        book = Book.objects.create(
            title="test",
            inventory=10,
            daily_fee=5.00
        )
        self.assertEqual(str(book), book.title)
