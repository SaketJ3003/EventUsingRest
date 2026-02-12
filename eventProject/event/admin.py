from django.contrib import admin
from .models import Category, Event, EventTag, EventImages

# Register your models here.
admin.site.register(Event)
admin.site.register(Category)
admin.site.register(EventTag)
admin.site.register(EventImages)