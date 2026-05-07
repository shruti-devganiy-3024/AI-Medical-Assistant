from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Appointment
        fields = [
            'id', 'doctor_name', 'date',
            'reason', 'status', 'created_at',
        ]
        read_only_fields = ['status', 'created_at']