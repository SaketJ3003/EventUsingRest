from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SignUpViewset, LoginViewSet, CategoryViewSet, EventTagViewSet, EventViewSet, RefreshTokenViewSet, EventListView, EventDetailView

router = DefaultRouter()
router.register(r'signup', SignUpViewset, basename='signup')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', EventTagViewSet, basename='tags')
router.register(r'events', EventViewSet, basename='events')
router.register(r'refreshToken', RefreshTokenViewSet, basename='refreshToken')

urlpatterns = [
    path('', include(router.urls)),
    path('template/events/', EventListView.as_view(), name='events-list'),
    path('template/events/<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
]