from django.db import models
from django.contrib.auth.models import User


class Appointment(models.Model):
    """
    Stores a single appointment booking.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor_name = models.CharField(max_length=120)
    date = models.DateTimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']  # show upcoming/recent first

    def __str__(self):
        return f"{self.user.username} - Dr. {self.doctor_name} ({self.date:%Y-%m-%d %H:%M})"