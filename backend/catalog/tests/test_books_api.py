from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from catalog.models import Book

BOOK_URL = reverse("catalog:book-list")


class BookApiTests(APITestCase):

    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="John Doe",
            cover="HARD",
            inventory=3,
            daily_fee=1.99
        )

    def test_list_books(self):
        response = self.client.get(BOOK_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_book(self):
        data = {
            "title": "New Book",
            "author": "Jane Smith",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": "2.50"
        }
        response = self.client.post(BOOK_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_retrieve_book(self):
        url = reverse("catalog:book-detail", args=[self.book.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book.title)

    def test_update_book(self):
        url = reverse("catalog:book-detail", args=[self.book.id])
        data = {"inventory": 10}
        response = self.client.patch(url, data)

        self.book.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book.inventory, 10)

    def test_delete_book(self):
        url = reverse("catalog:book-detail", args=[self.book.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
