from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('chat/', views.chat_page, name='chat'),
    path('appointment/', views.appointment_page, name='appointment'),
    path('history/', views.history_page, name='history'),
]