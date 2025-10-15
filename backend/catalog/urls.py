from django.urls import path, include
from .views import BookViewSet
from rest_framework import routers

app_name = "catalog"

router = routers.DefaultRouter()
router.register("books", BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
