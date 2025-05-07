from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('rider', 'Rider'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='rider')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

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
    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rider = models.ForeignKey(User, related_name='rides_as_rider', on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey(User, related_name='rides_as_driver', on_delete=models.SET_NULL, null=True, blank=True)
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.pk:
            old_ride = Ride.objects.get(pk=self.pk)
            old_status = old_ride.status
            
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
    id_ride_event = models.AutoField(primary_key=True)
    ride = models.ForeignKey(Ride, related_name='events', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Event {self.id_ride_event} for Ride {self.ride.id_ride}"

    class Meta:
        ordering = ['created_at']