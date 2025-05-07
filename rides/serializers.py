from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Ride, RideEvent
from django.db.models import Prefetch
from datetime import datetime, timedelta
import math

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Optimized to only include necessary fields for ride-related operations.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_active', 'password']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'rider'),
            phone_number=validated_data.get('phone_number', ''),
            is_active=True
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class RideEventSerializer(serializers.ModelSerializer):
    """
    Serializer for RideEvent model.
    Used for serializing ride events, particularly for the todays_ride_events field.
    """
    class Meta:
        model = RideEvent
        fields = ['id_ride_event', 'description', 'created_at']
        read_only_fields = ['id_ride_event', 'created_at']

class RideSerializer(serializers.ModelSerializer):
    """
    Serializer for Ride model with optimized related field handling.
    Includes nested serializers for rider, driver, and today's ride events.
    """
    rider = UserSerializer(read_only=True)
    driver = UserSerializer(read_only=True)
    rider_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='rider'),
        source='rider',
        write_only=True,
        required=True
    )
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='driver'),
        source='driver',
        write_only=True,
        required=False
    )
    todays_ride_events = serializers.SerializerMethodField()
    distance_to_pickup = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = '__all__'
        read_only_fields = ['id_ride', 'todays_ride_events', 'distance_to_pickup']

    def get_todays_ride_events(self, obj):
        """
        Returns ride events from the last 24 hours.
        This method is optimized to work with prefetch_related in the view.
        """
        # Check if todays_ride_events exists (it will be set by the Prefetch in the view)
        if not hasattr(obj, 'todays_ride_events'):
            return []
        return RideEventSerializer(obj.todays_ride_events, many=True).data

    def get_distance_to_pickup(self, obj):
        """
        Calculates the distance to pickup location from the provided GPS coordinates.
        Uses the Haversine formula for distance calculation.
        """
        request = self.context.get('request')
        if not request or 'latitude' not in request.query_params or 'longitude' not in request.query_params:
            return None

        try:
            lat1 = float(request.query_params['latitude'])
            lon1 = float(request.query_params['longitude'])
            lat2 = obj.pickup_latitude
            lon2 = obj.pickup_longitude

            # Haversine formula implementation using math functions
            R = 6371  # Earth's radius in kilometers
            dLat = math.radians(lat2 - lat1)
            dLon = math.radians(lon2 - lon1)
            a = (math.sin(dLat/2) * math.sin(dLat/2) +
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                 math.sin(dLon/2) * math.sin(dLon/2))
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c

            return round(distance, 2)  # Return distance in kilometers, rounded to 2 decimal places
        except (ValueError, TypeError):
            return None 