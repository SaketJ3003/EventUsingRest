from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    SignUpViewset, LoginViewSet, CategoryViewSet, EventTagViewSet, 
    EventViewSet, RefreshTokenViewSet, EventListView, EventDetailView, 
    SignUpTemplateView, LoginTemplateView, UserStatusViewSet, 
    CreateEventTemplateView, AdminDashboardView, AdminCategoriesView, 
    AdminTagsView, EditEventTemplateView, CountryViewSet, StateViewSet, 
    CityViewSet, AdminCountriesView, AdminStatesView, AdminCitiesView
)

router = DefaultRouter()
router.register(r'user-status', UserStatusViewSet, basename='user-status')
router.register(r'signup', SignUpViewset, basename='signup')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', EventTagViewSet, basename='tags')
router.register(r'events', EventViewSet, basename='events')
router.register(r'refreshToken', RefreshTokenViewSet, basename='refreshToken')
router.register(r'countries', CountryViewSet, basename='countries')
router.register(r'states', StateViewSet, basename='states')
router.register(r'cities', CityViewSet, basename='cities')

urlpatterns = [
    path('', include(router.urls)),
    path('template/events/', EventListView.as_view(), name='events-list'),
    path('template/events/<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('template/create-event/', CreateEventTemplateView.as_view(), name='create-event'),
    path('template/signup/', SignUpTemplateView.as_view(), name='signup-page'),
    path('template/login/', LoginTemplateView.as_view(), name='login-page'),
    
    # Admin pages
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/categories/', AdminCategoriesView.as_view(), name='admin-categories'),
    path('admin/tags/', AdminTagsView.as_view(), name='admin-tags'),
    path('admin/edit-event/', EditEventTemplateView.as_view(), name='edit-event'),
    path('admin/countries/', AdminCountriesView.as_view(), name='admin-countries'),
    path('admin/states/', AdminStatesView.as_view(), name='admin-states'),
    path('admin/cities/', AdminCitiesView.as_view(), name='admin-cities'),
]