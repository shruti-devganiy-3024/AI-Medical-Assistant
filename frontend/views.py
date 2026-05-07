from django.shortcuts import render


def index_page(request):
    """Login + Register combined page"""
    return render(request, 'index.html')


def dashboard_page(request):
    return render(request, 'dashboard.html')


def chat_page(request):
    return render(request, 'chat.html')


def appointment_page(request):
    return render(request, 'appointment.html')


def history_page(request):
    return render(request, 'history.html')