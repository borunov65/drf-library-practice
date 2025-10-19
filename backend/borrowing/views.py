from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import Borrowing
from .serializers import BorrowingListSerializer, BorrowingCreateSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user").all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.select_related("book", "user")

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        is_active_param = self.request.query_params.get("is_active")
        if is_active_param is not None:
            if is_active_param.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active_param.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
