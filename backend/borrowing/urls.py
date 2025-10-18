from django.urls import path, include
from .views import BorrowingViewSet
from rest_framework import routers

app_name = "borrowing"

router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
