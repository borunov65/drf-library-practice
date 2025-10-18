from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from catalog.models import Book
from user.models import User
from borrowing.models import Borrowing


class BorrowingReadOnlyTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="HARD",
            inventory=3,
            daily_fee=5
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2025-10-01",
            expected_return_date="2025-10-10"
        )
        self.url = reverse("borrowing:borrowing-list")

    def test_list_borrowings(self):
        """GET borrowings list works"""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn("results", res.data)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(len(res.data["results"]), 1)

        borrowing_data = res.data["results"][0]
        self.assertEqual(borrowing_data["book"]["title"], "Test Book")
        self.assertEqual(borrowing_data["user"]["email"], "user@example.com")
