from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (
        IsAuthenticated, IsOwner,
    )
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(
            reviewer=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            reviewer=self.request.user,
            ipaddr=self.request.META['REMOTE_ADDR']
        )
