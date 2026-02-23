from django.urls import path
from .views import (
    AdminDashboardView,
    AdminCategoriesView,
    AdminTagsView,
    EditEventTemplateView,
    CreateEventTemplateView,
    AdminCountriesView,
    AdminStatesView,
    AdminCitiesView,
)

urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('categories/', AdminCategoriesView.as_view(), name='admin-categories'),
    path('tags/', AdminTagsView.as_view(), name='admin-tags'),
    path('edit-event/', EditEventTemplateView.as_view(), name='edit-event'),
    path('create-event/', CreateEventTemplateView.as_view(), name='create-event'),
    path('countries/', AdminCountriesView.as_view(), name='admin-countries'),
    path('states/', AdminStatesView.as_view(), name='admin-states'),
    path('cities/', AdminCitiesView.as_view(), name='admin-cities'),
]
