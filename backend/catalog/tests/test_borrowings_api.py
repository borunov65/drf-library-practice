from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from user.models import User
from catalog.models import Book
from borrowing.models import Borrowing


class BaseBorrowingTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(email="user@example.com", password="password123")
        self.other_user = User.objects.create_user(email="other@example.com", password="password123")
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password="admin123")

        self.book1 = Book.objects.create(title="Book 1", author="Author 1", cover="HARD", inventory=3, daily_fee=5)
        self.book2 = Book.objects.create(title="Book 2", author="Author 2", cover="SOFT", inventory=2, daily_fee=4)
        self.book_out_of_stock = Book.objects.create(title="Out of Stock", author="Author 3", cover="SOFT", inventory=0, daily_fee=3)

        self.url = reverse("borrowing:borrowing-list")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)


class BorrowingReadOnlyTests(BaseBorrowingTestCase):
    def setUp(self):
        super().setUp()
        self.borrowing1 = Borrowing.objects.create(
            user=self.user, book=self.book1, borrow_date="2025-10-01", expected_return_date="2025-10-10"
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.other_user, book=self.book2, borrow_date="2025-10-05",
            expected_return_date="2025-10-15", actual_return_date="2025-10-12"
        )

    def test_authentication_required(self):
        """Non-authenticated users cannot see borrowings"""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_user_sees_only_their_own_borrowings(self):
        self.authenticate(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["user"]["email"], self.user.email)

    def test_admin_user_sees_all_borrowings(self):
        self.authenticate(self.admin_user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 2)

    def test_admin_user_can_filter_by_user_id(self):
        self.authenticate(self.admin_user)
        res = self.client.get(self.url, {"user_id": self.user.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["user"]["email"], self.user.email)

    def test_filter_by_is_active(self):
        self.authenticate(self.admin_user)
        res = self.client.get(self.url, {"is_active": "true"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data["results"]
        self.assertTrue(all(b["actual_return_date"] is None for b in results))


class BorrowingCreateTests(BaseBorrowingTestCase):
    def test_create_borrowing_success(self):
        self.authenticate(self.user)
        data = {
            "borrow_date": "2025-10-20",
            "expected_return_date": "2025-10-25",
            "book": self.book1.id
        }
        res = self.client.post(self.url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.book1.refresh_from_db()
        self.assertEqual(self.book1.inventory, 2)

        borrowing_id = res.data.get("id")
        self.assertIsNotNone(borrowing_id)
        borrowing = Borrowing.objects.get(id=borrowing_id)
        self.assertEqual(borrowing.user, self.user)

    def test_create_borrowing_fail_out_of_stock(self):
        self.authenticate(self.user)
        data = {
            "borrow_date": "2025-10-20",
            "expected_return_date": "2025-10-25",
            "book": self.book_out_of_stock.id
        }
        res = self.client.post(self.url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("book", res.data)
        self.assertEqual(res.data["book"][0], "This book is out of stock.")

    def test_non_authenticated_cannot_create_borrowing(self):
        data = {
            "borrow_date": "2025-10-20",
            "expected_return_date": "2025-10-25",
            "book": self.book1.id
        }
        res = self.client.post(self.url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class BorrowingReturnTests(BaseBorrowingTestCase):
    def setUp(self):
        super().setUp()
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book1,
            borrow_date="2025-10-10",
            expected_return_date="2025-10-20"
        )
        self.url_return = reverse("borrowing:borrowing-return-borrowing", args=[self.borrowing.id])

    def test_authenticated_user_can_return_book(self):
        """User can return their borrowing and inventory increases"""
        self.authenticate(self.user)
        res = self.client.post(self.url_return)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("message", res.data)
        self.assertEqual(res.data["message"], "Book returned successfully.")

        self.borrowing.refresh_from_db()
        self.book1.refresh_from_db()

        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.assertEqual(self.book1.inventory, 4)

    def test_cannot_return_twice(self):
        """User cannot return the same borrowing twice"""
        self.authenticate(self.user)
        self.client.post(self.url_return)  # first return
        res = self.client.post(self.url_return)  # second return

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)
        self.assertEqual(res.data["error"], "This borrowing has already been returned.")

    def test_unauthenticated_user_cannot_return(self):
        """Non-authenticated users cannot return a borrowing"""
        res = self.client.post(self.url_return)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_return_other_user_borrowing(self):
        """Admin user can return another user's borrowing"""
        self.authenticate(self.admin_user)
        res = self.client.post(self.url_return)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
