from rest_framework import serializers

from .models import Borrowing
from catalog.models import Book
from user.models import User


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "cover", "inventory", "daily_fee"]


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]


class BorrowingListSerializer(serializers.ModelSerializer):
    book = BookDetailSerializer(read_only=True)
    user = UserDetailSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active"
        ]

    def get_is_active(self, obj):
        return obj.actual_return_date is None


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book"
        ]

    def validate_book(self, book):
        if book.inventory <= 0:
            raise serializers.ValidationError("This book is out of stock.")
        return book

    def create(self, validated_data):
        user = self.context['request'].user
        book = validated_data['book']

        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(user=user, **validated_data)
        return borrowing
