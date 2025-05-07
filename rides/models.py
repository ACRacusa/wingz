from django.db import models
from django.contrib.auth.models import AbstractUser

# Using Django's built-in User model is often preferred,
# but the requirements specify a custom User table structure.
# We'll extend AbstractUser to get auth features but customize fields.
class User(AbstractUser):
    # Remove fields not specified in the requirements if extending AbstractUser
    # or create a completely custom user model if preferred.
    # For simplicity here, let's stick closer to the spec, assuming AbstractUser is okay.
    # If a completely separate User table is mandatory, we'd use models.Model
    # and handle authentication manually or with a different approach.

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('rider', 'Rider'),
        # Add other roles if needed, spec just mentions 'admin or other roles'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='rider')
    # first_name, last_name, email are inherited from AbstractUser
    phone_number = models.CharField(max_length=20, blank=True, null=True) # Spec says VARCHAR, assuming optional

    # Override default AbstractUser fields if needed, e.g., make email non-unique if required
    # For the assessment, let's assume standard AbstractUser fields suffice where overlapping

    # We need to tell Django to use this User model
    # This would typically go in settings.py: AUTH_USER_MODEL = 'rides.User'
    # We'll handle settings later.

    def __str__(self):
        return self.email


class Ride(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('en-route', 'En-Route'),
        ('pickup', 'Pickup'),
        ('dropoff', 'Dropoff'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    # Using id_ride as primary key name as per spec, though Django defaults to 'id'
    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # Using ForeignKey with the custom User model
    rider = models.ForeignKey(User, related_name='rides_as_rider', on_delete=models.SET_NULL, null=True, blank=True) # Renamed id_rider to rider
    driver = models.ForeignKey(User, related_name='rides_as_driver', on_delete=models.SET_NULL, null=True, blank=True) # Renamed id_driver to driver
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Check if this is an existing ride
        if self.pk:
            # Get the old status from the database
            old_ride = Ride.objects.get(pk=self.pk)
            old_status = old_ride.status
            
            # If status changed to pickup or dropoff, create an event
            if self.status != old_status:
                if self.status == 'pickup':
                    RideEvent.objects.create(
                        ride=self,
                        description='Status changed to pickup'
                    )
                elif self.status == 'dropoff':
                    RideEvent.objects.create(
                        ride=self,
                        description='Status changed to dropoff'
                    )
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ride {self.id_ride} ({self.status})"

class RideEvent(models.Model):
    # Using id_ride_event as primary key name
    id_ride_event = models.AutoField(primary_key=True)
    ride = models.ForeignKey(Ride, related_name='events', on_delete=models.CASCADE) # Renamed id_ride to ride
    description = models.CharField(max_length=255) # Increased length from VARCHAR assumption
    created_at = models.DateTimeField(auto_now_add=True) # auto_now_add sets timestamp on creation

    def __str__(self):
        return f"Event {self.id_ride_event} for Ride {self.ride.id_ride}"

    class Meta:
        ordering = ['created_at'] # Default ordering for ride events 