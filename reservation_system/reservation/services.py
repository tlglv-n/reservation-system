from reservation_system.reservation.models import Reservation, Queue


class ReservationService:
    @staticmethod
    def create_reservation(user, time_slot):
        reservation, created = Reservation.objects.get_or_create(time_slot=time_slot)
        if reservation.add_user(user):
            return "Reservation confirmed"
        else:
            queue, _ = Queue.objects.get_or_create(time_slot=time_slot)
            queue.add_user(user)
            return "Time slot is full, added to the queue"

    @staticmethod
    def cancel_reservation(user, time_slot):
        reservation = Reservation.objects.filter(time_slot=time_slot).first()
        if reservation:
            reservation.remove_user(user)
            return "Reservation cancelled"
        return "Reservation not found"

    @staticmethod
    def get_queue_size(time_slot):
        queue = Queue.objects.filter(time_slot=time_slot).first()
        if queue:
            return queue.queue_size()
        return 0

    @staticmethod
    def list_users_in_time_slot(time_slot):
        reservation = Reservation.objects.filter(time_slot=time_slot).first()
        if reservation:
            return reservation.users.all()
        return []
