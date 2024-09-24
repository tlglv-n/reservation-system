from django.utils import timezone
from email.utils import format_datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class Reservation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    reservation_time = models.DateTimeField(default=timezone.now)
    is_available_reservation = models.BooleanField(default=True)

    def __str__(self):
        return f"Reservation by {self.user} at {self.formatted_reservation_time}"

    @property
    def formatted_reservation_time(self):
        return format_datetime(self.reservation_time)

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.is_available_reservation:
                raise ValidationError("This time is already reserved.")
            self.is_available_reservation = False
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_available_reservation = True
        super().delete(*args, **kwargs)

class Queue(models.Model):
    time_slot = models.TimeField()
    users = models.ManyToManyField(User, blank=True, related_name='queues')

    def notify_user(self, reservation):
        if reservation.is_slot_available():
            for user in self.users.all():
                print(f"{user.username}, появилось место в {reservation.time_slot}")
                reservation.add_user(user)
                self.remove_user(user)

    def add_user(self, user):
        self.users.add(user)
        self.save()

    def remove_user(self, user):
        self.users.remove(user)
        self.save()

    def queue_size(self):
        return self.users.count()
