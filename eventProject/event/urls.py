from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    SignUpViewset, LoginViewSet, CategoryViewSet, EventTagViewSet, 
    EventViewSet, EventCardListViewSet, RefreshTokenViewSet, EventListView, EventDetailView, 
    SignUpTemplateView, LoginTemplateView, UserStatusViewSet, 
    CountryViewSet, StateViewSet, CityViewSet,EventCardViewSet
)

router = DefaultRouter()
router.register(r'user-status', UserStatusViewSet, basename='user-status')
router.register(r'signup', SignUpViewset, basename='signup')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', EventTagViewSet, basename='tags')
router.register(r'events', EventViewSet, basename='events')
router.register(r'event-cards-list', EventCardListViewSet, basename='event-cards-list')
router.register(r'event-cards', EventCardViewSet, basename='event-cards')
router.register(r'refreshToken', RefreshTokenViewSet, basename='refreshToken')
router.register(r'countries', CountryViewSet, basename='countries')
router.register(r'states', StateViewSet, basename='states')
router.register(r'cities', CityViewSet, basename='cities')

urlpatterns = [
    path('', include(router.urls)),
    path('template/events/', EventListView.as_view(), name='events-list'),
    path('template/events/<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('template/signup/', SignUpTemplateView.as_view(), name='signup-page'),
    path('template/login/', LoginTemplateView.as_view(), name='login-page'),
]