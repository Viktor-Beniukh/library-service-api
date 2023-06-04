from rest_framework import serializers

from book.models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
        )


class BookUpdateSerializer(BookSerializer):
    title = serializers.CharField(read_only=True)
    author = serializers.CharField(read_only=True)
    cover = serializers.ChoiceField(
        choices=Book.COVER_CHOICES, read_only=True
    )
