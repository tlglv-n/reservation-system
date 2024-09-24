from django.db.models.signals import post_save
from django.dispatch import receiver

from reservation_system.reservation.models import Reservation, Queue

@receiver(post_save, sender=Reservation)
def check_queue(sender, instance, **kwargs):
    queue = Queue.objects.filter(time_slot=instance.time_slot).first()
    if queue:
        queue.notify_user(instance)
