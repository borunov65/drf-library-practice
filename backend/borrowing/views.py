from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

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
        elif user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user__id=user_id)

        is_active_param = self.request.query_params.get("is_active")
        if is_active_param is not None:
            if is_active_param.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active_param.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            return Response(
                {"error": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.actual_return_date = timezone.now().date()
        borrowing.book.inventory += 1
        borrowing.book.save()
        borrowing.save()

        return Response(
            {"message": "Book returned successfully."},
            status=status.HTTP_200_OK,
        )
