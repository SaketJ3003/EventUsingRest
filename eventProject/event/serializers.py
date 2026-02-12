from tokenize import TokenError
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken
from .validators import validate_email, validate_email_login,validate_name,validate_password,validate_username
from .models import Category, Event, UserToken, EventTag, EventImages

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

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, trim_whitespace=False)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            validate_email_login(email)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        
        try:
            validate_password(password)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        

        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise serializers.ValidationError("Invalid password.")
            except User.DoesNotExist:
                raise serializers.ValidationError("Email Does Not Exist")
        else:
            raise serializers.ValidationError("Email and password are required.")

        data['user'] = user
        return data

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        
        # Storing Token for a user in database to provide single session per user
        UserToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }
        )
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, write_only=True)
    access = serializers.CharField(read_only=True)

    def validate_refresh(self, value):
        try:
            refresh = RefreshToken(value)
        except TokenError as e:
            raise serializers.ValidationError(f"Invalid or Token is Expired: {str(e)}")
        except InvalidToken as e:
            raise serializers.ValidationError(f"Invalid token format: {str(e)}")
        return value

    def new_access_token(self, refresh_token):
        try:
            refresh = RefreshToken(refresh_token)
            user = refresh.get('user_id')
            
            if not user:
                raise serializers.ValidationError("Unable to identify user from token")
            
            try:
                userObj = User.objects.get(id=user)
                user_token = UserToken.objects.get(user=userObj)
                
                if user_token.refresh_token != refresh_token:
                    raise serializers.ValidationError("This refresh token is no longer active. Please log in again.")
            except UserToken.DoesNotExist:
                raise serializers.ValidationError("No active session found. Please log in again.")
            
            # Generated new access token
            new_access = str(refresh.access_token)
            
            # Storing it in database
            user_token.access_token = new_access
            user_token.save(update_fields=['access_token', 'created_at'])
            
            return {
                'access': new_access,
            }
        except TokenError as e:
            raise serializers.ValidationError(f"Unable to generate new access token: {str(e)}")
        except InvalidToken as e:
            raise serializers.ValidationError(f"Invalid token: {str(e)}")

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
    tags = serializers.SerializerMethodField()
    extraImages = serializers.SerializerMethodField()
    country = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    venue = serializers.CharField(max_length=200)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    short_description = serializers.CharField(max_length=255)
    long_description = serializers.CharField()
    views_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def get_tags(self, obj):
        return list(obj.tags.values_list('name', flat=True))

    def get_extraImages(self, obj):
        request = self.context.get('request')
        images = list(obj.extraImages.values_list('image', flat=True))
        images = list(obj.extraImages.values_list('image', flat=True))
        
        if request:
            return [request.build_absolute_uri(f'/media/{image}') for image in images]
        return [f'/media/{image}' for image in images]

    def to_internal_value(self, data):
        self.tags_data = data.pop('tags', [])
        self.images_data = data.pop('extraImages', [])
        return super().to_internal_value(data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        if instance and hasattr(instance, 'category'):
            ret['category'] = list(instance.category.values_list('name', flat=True))
        
        request = self.context.get('request')
        if ret.get('feature_image') and request:
            ret['feature_image'] = request.build_absolute_uri(f'/media/{ret["feature_image"]}')
        
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
        tag_names = getattr(self, 'tags_data', [])
        images_data = getattr(self, 'images_data', [])
        
        categories = []
        for category_name in category_names:
            try:
                category = Category.objects.get(name=category_name)
                categories.append(category)
            except Category.DoesNotExist:
                raise serializers.ValidationError(f"Category '{category_name}' does not exist.")
        
        tags = []
        for tag_name in tag_names:
            if tag_name and tag_name.strip():
                tag, created = EventTag.objects.get_or_create(
                    name=tag_name
                )
                tags.append(tag)
        
        images = []
        if isinstance(images_data, list):
            for image in images_data:
                if image:
                    event_image = EventImages.objects.create(image=image)
                    images.append(event_image)
        
        title = validated_data.get('title')
        generated_slug = slugify(title)
        
        if Event.objects.filter(slug=generated_slug).exists():
            raise serializers.ValidationError({
                'title': f"An event with title '{title}' already exists."
            })
        
        validated_data['slug'] = generated_slug
        
        event = Event.objects.create(**validated_data)
        
        event.category.set(categories)
        event.tags.set(tags)
        event.extraImages.set(images)
        
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
        
        if hasattr(self, 'tags_data'):
            tag_names = self.tags_data
            tags = []
            for tag_name in tag_names:
                if tag_name and tag_name.strip():
                    tag, created = EventTag.objects.get_or_create(
                        name=tag_name
                    )
                    tags.append(tag)
            instance.tags.set(tags)
        
        if hasattr(self, 'images_data'):
            images_data = self.images_data
            images = []
            if isinstance(images_data, list):
                for image in images_data:
                    if image:
                        event_image = EventImages.objects.create(image=image)
                        images.append(event_image)
            instance.extraImages.set(images)
        
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
    
    