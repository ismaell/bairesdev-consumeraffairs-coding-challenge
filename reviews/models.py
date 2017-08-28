from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):
    title = models.CharField(max_length=64)
    summary = models.CharField(max_length=100000)
    rating = models.PositiveIntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1),
        ]
    )
    ipaddr = models.GenericIPAddressField()
    submission_date = models.DateTimeField(auto_now_add=True)
    company = models.CharField(max_length=64)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE)
