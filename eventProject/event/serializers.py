from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify
from .validators import validate_email,validate_name,validate_password,validate_username
from .models import Category, Event

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(trim_whitespace=False)
    first_name = serializers.CharField(allow_blank = True,trim_whitespace=False)
    last_name = serializers.CharField(trim_whitespace=False)
    email = serializers.CharField(trim_whitespace=False)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name','last_name','email','password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data, password=password)
        return user
    
    def validate_username(self, value):
        try:
            return validate_username(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def validate_first_name(self, value):
        try:
            return validate_name(value, allow_spaces=False, field_name="First name")
        except ValueError as e:
            raise serializers.ValidationError(str(e))
    
    def validate_last_name(self, value):
        try:
            return validate_name(value, allow_spaces=False, field_name="First name")
        except ValueError as e:
            raise serializers.ValidationError(str(e))
    
    def validate_email(self, value):
        try:
            return validate_email(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
    
    def validate_password(self, value):
        try:
            return validate_password(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    isActive =serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    slug = serializers.SlugField(read_only=True)
    feature_image = serializers.ImageField(required=False, allow_null=True)
    category = serializers.JSONField()
    country = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    venue = serializers.CharField(max_length=200)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    is_active = serializers.BooleanField(default=True)
    short_description = serializers.CharField(max_length=255)
    long_description = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance and hasattr(instance, 'category'):
            ret['category'] = list(instance.category.values_list('name', flat=True))
        return ret
    
    def validate_category(self, value):
        if not value or not isinstance(value, list):
            raise serializers.ValidationError("Category must be a list of category names.")
        
        if len(value) == 0:
            raise serializers.ValidationError("At least one category is required.")
        
        for category_name in value:
            if not category_name or not category_name.strip():
                raise serializers.ValidationError("Category name cannot be empty.")
            
            if not Category.objects.filter(name=category_name).exists():
                raise serializers.ValidationError(f"Category '{category_name}' does not exist.")
        
        return value

    def create(self, validated_data):
        category_names = validated_data.pop('category')
        
        categories = []
        for category_name in category_names:
            try:
                category = Category.objects.get(name=category_name)
                categories.append(category)
            except Category.DoesNotExist:
                raise serializers.ValidationError(f"Category '{category_name}' does not exist.")
        
        title = validated_data.get('title')
        generated_slug = slugify(title)
        
        if Event.objects.filter(slug=generated_slug).exists():
            raise serializers.ValidationError({
                'title': f"An event with title '{title}' already exists."
            })
        
        validated_data['slug'] = generated_slug
        
        event = Event.objects.create(**validated_data)
        
        event.category.set(categories)
        
        return event

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        
        if 'title' in validated_data:
            instance.slug = slugify(validated_data['title'])
        
        if 'feature_image' in validated_data:
            instance.feature_image = validated_data.get('feature_image')
        
        if 'category' in validated_data:
            category_names = validated_data.get('category')
            categories = []
            for category_name in category_names:
                try:
                    category = Category.objects.get(name=category_name)
                    categories.append(category)
                except Category.DoesNotExist:
                    raise serializers.ValidationError(f"Category '{category_name}' does not exist.")
            
            instance.category.set(categories)
        
        instance.country = validated_data.get('country', instance.country)
        instance.state = validated_data.get('state', instance.state)
        instance.city = validated_data.get('city', instance.city)
        instance.venue = validated_data.get('venue', instance.venue)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.long_description = validated_data.get('long_description', instance.long_description)
        instance.save()
        return instance
    
    