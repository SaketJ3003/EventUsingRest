from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SignUpViewset, CategoryViewSet, EventViewSet

router = DefaultRouter()
router.register(r'signup', SignUpViewset, basename='signup')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]