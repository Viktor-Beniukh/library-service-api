from django.db import models


class Book(models.Model):
    HARD = "HARD"
    SOFT = "SOFT"

    COVER_CHOICES = [
        (HARD, "Hard"),
        (SOFT, "Soft")
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    cover = models.CharField(
        max_length=20, choices=COVER_CHOICES, default=HARD
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title
