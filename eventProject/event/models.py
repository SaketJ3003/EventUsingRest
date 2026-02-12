from django.db import models
from django.contrib.auth.models import User


class UserToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='active_token')
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Token for {self.user.username}"


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    isActive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EventTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EventImages(models.Model):
    image = models.ImageField(upload_to='events/extra-images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Event Image - {self.id}"

class Event(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    feature_image = models.ImageField(upload_to='events/', blank=True, null=True)
    category = models.ManyToManyField(Category, related_name='events')
    tags = models.ManyToManyField(EventTag, related_name='events', blank=True)
    extraImages = models.ManyToManyField(EventImages, related_name='events', blank=True)
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=15)
    venue = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    short_description = models.CharField(max_length=255)
    long_description = models.TextField()
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
