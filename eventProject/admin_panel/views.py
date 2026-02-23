from django.shortcuts import render
from django.views import View
from event.models import Event, Category, EventTag


class AdminDashboardView(View):
    def get(self, request):
        context = {
            'events_count': Event.objects.count(),
            'categories_count': Category.objects.count(),
            'tags_count': EventTag.objects.count(),
        }
        return render(request, 'admin_panel/admin_dashboard.html', context)


class AdminCategoriesView(View):
    def get(self, request):
        return render(request, 'admin_panel/admin_categories.html')


class AdminTagsView(View):
    def get(self, request):
        return render(request, 'admin_panel/admin_tags.html')


class EditEventTemplateView(View):
    def get(self, request):
        return render(request, 'admin_panel/edit_event.html')


class CreateEventTemplateView(View):
    def get(self, request):
        return render(request, 'admin_panel/create_event.html')


class AdminCountriesView(View):
    def get(self, request):
        return render(request, 'admin_panel/admin_countries.html')


class AdminStatesView(View):
    def get(self, request):
        return render(request, 'admin_panel/admin_states.html')


class AdminCitiesView(View):
    def get(self, request):
        return render(request, 'admin_panel/admin_cities.html')

