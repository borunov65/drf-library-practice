from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from catalog.models import Book


BOOK_URL = reverse("catalog:book-list")


class IsAdminOrReadOnlyPermissionTests(APITestCase):
    """Tests for IsAdminOrReadOnly permission."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="user", password="testpass123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpass123", email="admin@example.com"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="John Doe",
            cover="HARD",
            inventory=3,
            daily_fee=1.99
        )

    def test_any_user_can_list_books(self):

        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_create_book(self):
        data = {
            "title": "New Book",
            "author": "Jane Smith",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": "2.50"
        }

        response = self.client.post(BOOK_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_user_cannot_create_book(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New Book",
            "author": "Jane Smith",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": "2.50"
        }

        response = self.client.post(BOOK_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_book(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "title": "Admin Book",
            "author": "Admin Author",
            "cover": "SOFT",
            "inventory": 7,
            "daily_fee": "3.00"
        }

        response = self.client.post(BOOK_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_non_admin_user_can_only_read(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("catalog:book-detail", args=[self.book.id])

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        patch_response = self.client.patch(url, {"inventory": 10})
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
