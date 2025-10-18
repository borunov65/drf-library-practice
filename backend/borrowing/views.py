from rest_framework import viewsets, mixins
from .models import Borrowing
from .serializers import BorrowingListSerializer
from catalog.permissions import IsAdminOrReadOnly


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user").all()
    serializer_class = BorrowingListSerializer
    permission_classes = [IsAdminOrReadOnly]
