from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """
    Validates registration data and creates a new user.
    """
    password = serializers.CharField(
        write_only=True,    # never show password in API responses
        min_length=6
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # create_user() automatically hashes the password 
        return User.objects.create_user(**validated_data)