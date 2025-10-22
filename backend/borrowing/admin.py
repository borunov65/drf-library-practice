from django.contrib import admin

from .models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = [
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "book",
        "user_name",
    ]
    list_filter = [
        "borrow_date",
        "expected_return_date",
        "actual_return_date"
    ]
    search_fields = [
        "book__title",
        "user__first_name",
        "user__last_name",
        "user__email"
    ]

    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} {obj.user.email}"

    user_name.short_description = "User"
