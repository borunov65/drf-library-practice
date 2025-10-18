from django.db import models
from django.db.models import Q, F

from catalog.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "borrowings"
        constraints = [
            models.CheckConstraint(
                check=Q(expected_return_date__gt=F('borrow_date')),
                name='expected_after_borrow'
            ),
            models.CheckConstraint(
                check=Q(actual_return_date__isnull=True) |
                      Q(actual_return_date__gte=F('borrow_date')),
                name='actual_after_borrow'
            ),
        ]

    def __str__(self):
        returned = self.actual_return_date or "not returned yet"
        return (
            f"{self.user.first_name} {self.user.last_name} "
            f"({self.user.email}) borrowed '{self.book.title}' "
            f"on {self.borrow_date}, returned: {returned}"
        )
