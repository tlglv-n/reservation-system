from pyexpat.errors import messages

from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status

from reservation_system import reservation
from reservation_system.reservation.models import Queue, Reservation
from reservation_system.reservation.services import ReservationService

queue = {}

def user_list(request):
    context = {
        'users': User.objects.all()
    }
    return render(request, "reservations/user_list", context)


def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {
        'user': user,
        'slot_time': Reservation.objects.filter(user=user)
    }
    return render(request, 'reservations/user_detail', context)


def user_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-reservation_time')
    context = {
        'reservations': reservations
    }
    return render(request, 'reservations/user_reservations', context)


def reservation_form(request, slot_time):
    reservation_obj = get_object_or_404(Reservation, pk=slot_time)
    users = User.objects.all()

    context = {
        'reservation_time': reservation_obj,
        'users': users
    }

    if request.method == 'POST':
        users_id = request.POST.getlist('users')
        if not users_id:
            messages.error(request, "Please select at least one user.")
            return render(request, 'reservations/reservation_form.html', context)

        unavailable_time = []
        for user_id in users_id:
            user = get_object_or_404(User, pk=user_id)
            if not reservation_obj.is_available_reservation:
                unavailable_time.append(user.username)

        if unavailable_time:
            messages.error(request, f"Time for {', '.join(unavailable_time)} is no longer available.")
            return render(request, 'reservations/reservation_form.html', context)

        for user_id in users_id:
            user = get_object_or_404(User, pk=user_id)
            Reservation.objects.create(user=user, reservation_time=reservation_obj.reservation_time)

        messages.success(request, "Time reserved successfully!")
        return redirect('user_list')

    return render(request, 'reservations/reservation_form.html', context)



class QueueView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        time_slot = data.get('time_slot')
        user = data.get('user')

        if not time_slot or not user:
            return Response({"error": "time_slot and user are required"}, status=status.HTTP_400_BAD_REQUEST)

        if time_slot not in queue:
            queue[time_slot] = []

        queue[time_slot].append(user)
        position = len(queue[time_slot])

        return Response({
            "message": f"User {user} added to the queue for {time_slot}.",
            "position": position
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        data = request.data
        time_slot = data.get('time_slot')
        user = data.get('user')

        if not time_slot or not user or time_slot not in queue or user not in queue[time_slot]:
            return Response({"error": "Invalid time_slot or user not in queue"}, status=status.HTTP_400_BAD_REQUEST)

        queue[time_slot].remove(user)

        return Response({"message": f"User {user} removed from the queue for {time_slot}."})

    def get(self, request, *args, **kwargs):
        time_slot = request.query_params.get('time_slot')

        if not time_slot or time_slot not in queue:
            return Response({"error": "No queue for this time slot"}, status=status.HTTP_400_BAD_REQUEST)

        queue_list = [{"user": user, "position": index + 1} for index, user in enumerate(queue[time_slot])]

        return Response({"time_slot": time_slot, "queue": queue_list})
