from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch, Q
from datetime import datetime, timedelta
from .models import Ride, RideEvent, User
from .serializers import RideSerializer, UserSerializer, RideEventSerializer
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsAdminOrDriverUser(permissions.BasePermission):
    """
    Custom permission to allow admin and driver users to access the API.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role in ['admin', 'driver']

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access user management.
    """
    def has_permission(self, request, view):
        if view.action == 'me':
            return bool(request.user and request.user.is_authenticated)
        return request.user and request.user.role == 'admin'

class RideViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ride model with optimized queries and filtering.
    Implements all required functionality including:
    - Pagination
    - Filtering by status and rider email
    - Sorting by pickup_time and distance to pickup
    - Efficient retrieval of today's ride events
    """
    serializer_class = RideSerializer
    permission_classes = [IsAdminOrDriverUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'rider__email']
    ordering_fields = ['pickup_time', 'distance_to_pickup']
    ordering = ['-pickup_time']  # Default ordering

    def get_queryset(self):
        """
        Returns an optimized queryset with:
        - Prefetched related rider and driver using select_related
        - Prefetched today's ride events using prefetch_related
        - Support for distance-based sorting
        
        Query Optimization:
        1. select_related('rider', 'driver'):
           - Fetches rider and driver data in a single query using SQL JOIN
           - Reduces N+1 query problem for related user data
           - Example: Without select_related, each ride would trigger a separate query for rider and driver
        
        2. prefetch_related(todays_events):
           - Fetches today's ride events in a separate query
           - Uses Prefetch object to filter events to last 24 hours
           - Example: Without prefetch_related, each ride would trigger a separate query for events
        
        Total Queries:
        - 1 query for rides with related rider/driver (select_related)
        - 1 query for today's events (prefetch_related)
        - 1 query for count (pagination)
        Total: 3 queries regardless of number of rides
        """
        # Base queryset with select_related for foreign keys
        # This creates a single query with JOINs for rider and driver
        queryset = Ride.objects.select_related('rider', 'driver')

        # Prefetch today's ride events (last 24 hours)
        # This creates a separate query for events but is more efficient than
        # fetching all events or making a query per ride
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        todays_events = Prefetch(
            'events',  # The related name for RideEvent
            queryset=RideEvent.objects.filter(created_at__gte=yesterday),
            to_attr='todays_ride_events'  # Store results in this attribute
        )
        queryset = queryset.prefetch_related(todays_events)

        # Handle distance-based sorting if requested
        ordering = self.request.query_params.get('ordering', '')
        if 'distance_to_pickup' in ordering:
            lat = self.request.query_params.get('latitude')
            lon = self.request.query_params.get('longitude')
            if lat and lon:
                # Add distance annotation using simplified Haversine formula
                queryset = queryset.extra(
                    select={
                        'distance_to_pickup': """
                            6371 * 2 * ASIN(
                                SQRT(
                                    POWER(SIN(RADIANS(%s - pickup_latitude) / 2), 2) +
                                    COS(RADIANS(pickup_latitude)) * 
                                    COS(RADIANS(%s)) * 
                                    POWER(SIN(RADIANS(%s - pickup_longitude) / 2), 2)
                                )
                            )
                        """
                    },
                    select_params=[lat, lat, lon]
                )

        return queryset

    def get_serializer_context(self):
        """
        Adds request context to serializer for distance calculation.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model with CRUD operations.
    Only admin users can manage other users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get the current user's information
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
