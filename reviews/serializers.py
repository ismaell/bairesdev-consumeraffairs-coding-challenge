from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Review
        fields = (
            'title',
            'summary',
            'rating',
            'company',
            'submission_date',
            'reviewer',
            'ipaddr',
            'id',
        )
    submission_date = serializers.DateTimeField(read_only=True)
    reviewer = serializers.CharField(read_only=True)
    ipaddr = serializers.CharField(read_only=True)
