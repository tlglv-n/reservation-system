from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('<int:pk>/', views.user_detail, name='user_detail'),
    path('reservation/<int:slot_time>/', views.reservation_form, name='reservation_form'),
    path('reservations/', views.user_reservations, name='user_reservations'),
]
