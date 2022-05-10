"""Defines three models used throughout the project.

A model is a subclass of models.Model. Each model defined below maps
to one database table. Each class field map to a database field. Each
instance fills one row in the database.
"""


import datetime

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Ticket(models.Model):
    """Tickets created by the end-user are stored in the DB through this model.

    has_review ...
    """
    title: str = models.CharField(max_length=128)
    description: str = models.TextField(max_length=2048, blank=True)
    user: User = models.ForeignKey(to=User, on_delete=models.CASCADE)
    time_created: datetime.datetime = models.DateTimeField(auto_now_add=True)
    has_review: bool = models.BooleanField(blank=True, default=False)

    def __str__(self) -> str:
        return self.title


class Review(models.Model):
    """Reviews created by the end-user are stored in the DB through this model.
    """
    ticket: str = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating: int = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    headline: str = models.CharField(max_length=128)
    body: str = models.TextField(max_length=8192, blank=True)
    user: User = models.ForeignKey(
        to=User, on_delete=models.CASCADE
    )
    time_created: bool = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.headline


class UserFollows(models.Model):
    user: User = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='following')
    followed_user: User = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="followed_by"
    )

    class Meta:
        """ensures user x cannot follow user y twice."""
        unique_together = ('user', "followed_user")
