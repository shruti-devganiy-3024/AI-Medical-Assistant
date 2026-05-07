from django.urls import path
from . import views

urlpatterns = [
    path('doctors/',              views.doctor_list,         name='doctor_list'),
    path('appointments/',         views.appointment_list,    name='appointment_list'),
    path('appointments/create/',  views.create_appointment,  name='create_appointment'),
    path('appointments/<int:apt_id>/cancel/',
                                  views.cancel_appointment,  name='cancel_appointment'),
]