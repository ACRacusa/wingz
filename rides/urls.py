from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import RideViewSet, UserViewSet, RideEventViewSet

# Create the main router
router = DefaultRouter()
router.register(r'rides', RideViewSet)
router.register(r'users', UserViewSet)

# Create a nested router for ride events
rides_router = routers.NestedDefaultRouter(router, r'rides', lookup='ride')
rides_router.register(r'events', RideEventViewSet, basename='ride-events')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(rides_router.urls)),
] 