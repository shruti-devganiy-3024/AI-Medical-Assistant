from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import Appointment
from .serializers import AppointmentSerializer


# ── Hardcoded doctors list ────────────────────────────────
# In a real app this would be a Doctor model in the DB.
# For now, a clean list is enough to show smart slot logic.
DOCTORS = [
    {
        'id': 1,
        'name': 'Dr. Sarah Ahmed',
        'specialization': 'General Physician',
        'available_days': [0, 1, 2, 3, 4],   # Mon–Fri
        'slots': ['09:00', '09:30', '10:00', '10:30',
                  '11:00', '11:30', '14:00', '14:30',
                  '15:00', '15:30', '16:00', '16:30'],
    },
    {
        'id': 2,
        'name': 'Dr. James Wilson',
        'specialization': 'Internal Medicine',
        'available_days': [0, 2, 4],           # Mon, Wed, Fri
        'slots': ['10:00', '10:30', '11:00',
                  '15:00', '15:30', '16:00'],
    },
    {
        'id': 3,
        'name': 'Dr. Priya Sharma',
        'specialization': 'Pulmonologist',
        'available_days': [1, 3],              # Tue, Thu
        'slots': ['09:00', '09:30', '10:00',
                  '14:00', '14:30', '15:00'],
    },
    {
        'id': 4,
        'name': 'Dr. Ali Hassan',
        'specialization': 'Cardiologist',
        'available_days': [0, 1, 2, 3, 4],
        'slots': ['11:00', '11:30', '12:00',
                  '16:00', '16:30', '17:00'],
    },
    {
        'id': 5,
        'name': 'Dr. Emily Chen',
        'specialization': 'Dermatologist',
        'available_days': [1, 2, 3, 4],        # Tue–Fri
        'slots': ['09:00', '09:30', '10:00',
                  '13:00', '13:30', '14:00'],
    },
]


# ── GET /api/doctors/ ─────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_list(request):
    """
    Returns list of doctors with their available slots.
    Marks slots as 'booked' if already taken for that date.
    """
    date_str = request.query_params.get('date', '')

    result = []
    for doc in DOCTORS:
        slots_info = []

        for slot in doc['slots']:
            is_booked = False

            if date_str:
                # Check if this slot is already booked
                is_booked = Appointment.objects.filter(
                    doctor_name=doc['name'],
                    date__date=date_str,
                    date__time=slot + ':00',
                    status__in=['pending', 'confirmed'],
                ).exists()

            slots_info.append({
                'time':      slot,
                'is_booked': is_booked,
            })

        result.append({
            'id':             doc['id'],
            'name':           doc['name'],
            'specialization': doc['specialization'],
            'available_days': doc['available_days'],
            'slots':          slots_info,
        })

    return Response(result)


# ── POST /api/appointments/ ───────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_appointment(request):
    """
    Books a new appointment.

    Body:
    {
        "doctor_name": "Dr. Sarah Ahmed",
        "date": "2025-05-10",
        "time": "10:00",
        "reason": "fever and cough",
        "full_name": "John Doe",
        "phone": "0300-1234567",
        "email": "john@example.com",
        "is_emergency": false
    }
    """
    data = request.data

    # ── Validate required fields ──────────────────────────
    required = ['doctor_name', 'date', 'time', 'full_name', 'phone']
    for field in required:
        if not data.get(field, '').strip():
            return Response(
                {'error': f'{field.replace("_", " ").title()} is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    date_str  = data.get('date', '').strip()
    time_str  = data.get('time', '').strip()
    is_emergency = data.get('is_emergency', False)

    # ── Combine date + time into datetime ─────────────────
    try:
        from datetime import datetime
        import pytz
        naive_dt  = datetime.strptime(
            f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
        )
        aware_dt  = timezone.make_aware(naive_dt)
    except ValueError:
        return Response(
            {'error': 'Invalid date or time format.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── No past appointments (unless emergency) ───────────
    if not is_emergency and aware_dt < timezone.now():
        return Response(
            {'error': 'Cannot book an appointment in the past.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── Check slot not already taken (unless emergency) ───
    if not is_emergency:
        already_booked = Appointment.objects.filter(
            doctor_name=data['doctor_name'],
            date=aware_dt,
            status__in=['pending', 'confirmed'],
        ).exists()

        if already_booked:
            return Response(
                {'error': 'This slot is already booked. Please choose another time.'},
                status=status.HTTP_409_CONFLICT
            )

    # ── Create appointment ────────────────────────────────
    appointment = Appointment.objects.create(
        user=request.user,
        doctor_name=data['doctor_name'],
        date=aware_dt,
        reason=data.get('reason', '').strip(),
        status='pending',
    )

    return Response(
        {
            'message':    'Appointment booked successfully!',
            'id':         appointment.id,
            'doctor':     appointment.doctor_name,
            'date':       date_str,
            'time':       time_str,
            'is_emergency': is_emergency,
        },
        status=status.HTTP_201_CREATED
    )


# ── GET /api/appointments/ ────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    """Returns all appointments for logged-in user."""
    appointments = Appointment.objects.filter(user=request.user)
    serializer   = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


# ── DELETE /api/appointments/<id>/ ───────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, apt_id):
    """Cancels (deletes) an appointment."""
    try:
        apt = Appointment.objects.get(id=apt_id, user=request.user)
    except Appointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    apt.delete()
    return Response(
        {'message': 'Appointment cancelled.'},
        status=status.HTTP_200_OK
    )