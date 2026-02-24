from tokenize import TokenError
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken
from .validators import validate_email, validate_email_login,validate_name,validate_password,validate_username
from .models import Category, Event, UserToken, EventTag, EventImages, Country, State, City
import os
from datetime import date

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
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
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

    def validate_email(self, value):
        try:
            return validate_email_login(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
    
    def validate_password(self, value):
        try:
            return validate_password(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        errors = {}
        
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                errors['password'] = "Invalid password."
        except User.DoesNotExist:
            errors['email'] = "Email does not exist. Please sign up first."
        
        if errors:
            raise serializers.ValidationError(errors)

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
            
            # Generated new access token from Refresh Token
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
    name = serializers.CharField(allow_blank = True,trim_whitespace=False, max_length=20)
    slug = serializers.SlugField(read_only=True)
    isActive =serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_name(self,value):
        try:
            return validate_name(value, allow_spaces=True, field_name="name")
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # print(instance)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class EventTagSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(allow_blank = True,trim_whitespace=False, max_length=20)
    slug = serializers.SlugField(read_only=True)
    isActive = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_name(self,value):
        try:
            return validate_name(value, allow_spaces=True, field_name="name")
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        return EventTag.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.isActive = validated_data.get('isActive', instance.isActive)
        instance.save()
        return instance


class CountrySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    slug = serializers.SlugField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_name(self, value):
        from .models import Country
        if not self.instance:
            if Country.objects.filter(name=value).exists():
                raise serializers.ValidationError("A country with this name already exists.")
        elif self.instance:
            if Country.objects.filter(name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("A country with this name already exists.")
        return value.title()

    def create(self, validated_data):
        return Country.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class StateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    slug = serializers.SlugField(read_only=True)
    country = serializers.IntegerField(write_only=True)
    country_detail = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_country(self, value):
        from .models import Country
        if not Country.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"Country with id {value} does not exist.")
        return value

    def validate(self, data):
        from .models import State
        if not self.instance: 
            if State.objects.filter(name=data['name'], country_id=data['country']).exists():
                raise serializers.ValidationError({"name": "A state with this name already exists in this country."})
        elif self.instance:
            if State.objects.filter(name=data.get('name', self.instance.name), 
                                   country_id=data.get('country', self.instance.country_id)).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({"name": "A state with this name already exists in this country."})
        return data

    def get_country_detail(self, obj):
        return {'id': obj.country.id, 'name': obj.country.name}

    def create(self, validated_data):
        country_id = validated_data.pop('country')
        return State.objects.create(country_id=country_id, **validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.country_id = validated_data.get('country', instance.country_id)
        instance.save()
        return instance


class CitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    slug = serializers.SlugField(read_only=True)
    state = serializers.IntegerField(write_only=True)
    state_detail = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_state(self, value):
        from .models import State
        if not State.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"State with id {value} does not exist.")
        return value

    def validate(self, data):
        from .models import City
        if not self.instance: 
            if City.objects.filter(name=data['name'], state_id=data['state']).exists():
                raise serializers.ValidationError({"name": "A city with this name already exists in this state."})
        elif self.instance:
            if City.objects.filter(name=data.get('name', self.instance.name), 
                                  state_id=data.get('state', self.instance.state_id)).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError({"name": "A city with this name already exists in this state."})
        return data

    def get_state_detail(self, obj):
        return {'id': obj.state.id, 'name': obj.state.name, 'country': {'id': obj.state.country.id, 'name': obj.state.country.name}}

    def create(self, validated_data):
        state_id = validated_data.pop('state')
        return City.objects.create(state_id=state_id, **validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.state_id = validated_data.get('state', instance.state_id)
        instance.save()
        return instance


class EventCardListSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True)
    title = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    feature_image = serializers.SerializerMethodField()
    event_date = serializers.DateField(read_only=True)
    city = serializers.SerializerMethodField()
    views_count = serializers.IntegerField(read_only=True)
    category = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    def get_feature_image(self, obj):
        if obj.feature_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.feature_image.url)
            return obj.feature_image.url
        return None

    def get_city(self, obj):
        if obj.city:
            return {'id': obj.city.id, 'name': obj.city.name}
        return None

    def get_state(self, obj):
        if obj.state:
            return {'id': obj.state.id, 'name': obj.state.name}
        return None

    def get_category(self, obj):
        return [{'id': cat.id, 'name': cat.name} for cat in obj.category.all()]

    def get_tags(self, obj):
        return [{'id': tag.id, 'name': tag.name} for tag in obj.tags.all()]
    
class EventCardSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True)
    title = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    short_description = serializers.CharField(read_only=True)
    feature_image = serializers.SerializerMethodField()
    event_date = serializers.DateField(read_only=True)
    start_time = serializers.TimeField(read_only=True)
    end_time = serializers.TimeField(read_only=True)
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    views_count = serializers.IntegerField(read_only=True)

    def get_feature_image(self, obj):
        if obj.feature_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.feature_image.url)
            return obj.feature_image.url
        return None

    def get_city(self, obj):
        if obj.city:
            return {'id': obj.city.id, 'name': obj.city.name}
        return None

    def get_state(self, obj):
        if obj.state:
            return {'id': obj.state.id, 'name': obj.state.name}
        return None

class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(allow_blank = True, trim_whitespace=False, max_length=100)
    slug = serializers.SlugField(required=False, allow_blank=True)
    feature_image = serializers.FileField(required=False)
    category = serializers.ListField(child=serializers.IntegerField(), required=True, allow_empty = False, write_only=True)
    tags = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty = True, write_only=True)
    extraImages = serializers.ListField(child=serializers.FileField(), required=False, allow_empty=True, write_only=True)
    country = serializers.IntegerField(write_only=True)
    state = serializers.IntegerField(write_only=True)
    city = serializers.IntegerField(write_only=True)
    venue = serializers.CharField(trim_whitespace=False, allow_blank = True, max_length=200)
    event_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    is_active = serializers.BooleanField(default=True)
    short_description = serializers.CharField(trim_whitespace=False, allow_blank = True, max_length=255)
    long_description = serializers.CharField(trim_whitespace=False, allow_blank = True)
    views_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        event_date = data.get('event_date')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError({
                    'end_time': "End Time should be greater than start time."
                })        
        return data
    
    def validate_event_date(self, value):
        if value:
            if value < date.today():
                raise serializers.ValidationError("Event Date should be greater than Today's Date")
        return value

    def validate_country(self, value):
        if not value:
            raise serializers.ValidationError("Country is required")
        if not Country.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Country with ID {value} does not exist")
        return value
    
    def validate_state(self, value):
        if not value:
            raise serializers.ValidationError("State is required")
        if not State.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"State with ID {value} does not exist")
        return value
    
    def validate_city(self, value):
        if not value:
            raise serializers.ValidationError("City is required")
        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"City with ID {value} does not exist")
        return value

    def get_feature_image(self, obj):
        if obj.feature_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.feature_image.url)
            return obj.feature_image.url
        return None

    def get_extraImages(self, obj):
        request = self.context.get('request')
        images = list(obj.extraImages.values_list('image', flat=True))
        
        if request:
            return [request.build_absolute_uri(f'/media/{image}') for image in images]
        return [f'/media/{image}' for image in images]

    def to_internal_value(self, data):
        # print(data)
        result = super().to_internal_value(data)
        # print(result)
        self.tags_data = result.pop('tags', [])
        self.images_data = result.pop('extraImages', [])
        
        self.remove_feature_image_flag = data.get('remove_feature_image', 'false') == 'true'
        if hasattr(data, 'getlist'):
            self.remove_extra_image_paths = data.getlist('remove_extra_images')
        else:
            val = data.get('remove_extra_images', [])
            self.remove_extra_image_paths = val if isinstance(val, list) else ([val] if val else [])
        
        return result

    def to_representation(self, instance):
        res = super().to_representation(instance)
        
        if instance and hasattr(instance, 'category'):
            res['category'] = list(instance.category.values('id', 'name','isActive'))
        
        if instance and hasattr(instance, 'tags'):
            res['tags'] = list(instance.tags.values('id', 'name','isActive'))
        
        if instance and hasattr(instance, 'country') and instance.country:
            res['country'] = {'id': instance.country.id, 'name': instance.country.name, 'slug': instance.country.slug}
        
        if instance and hasattr(instance, 'state') and instance.state:
            res['state'] = {'id': instance.state.id, 'name': instance.state.name, 'slug': instance.state.slug}
        
        if instance and hasattr(instance, 'city') and instance.city:
            res['city'] = {'id': instance.city.id, 'name': instance.city.name, 'slug': instance.city.slug}
        
        request = self.context.get('request')
        
        if instance and hasattr(instance, 'feature_image') and instance.feature_image:
            if request:
                res['feature_image'] = request.build_absolute_uri(instance.feature_image.url)
            else:
                res['feature_image'] = instance.feature_image.url
        
        if instance and hasattr(instance, 'extraImages'):
            images = list(instance.extraImages.values_list('image', flat=True))
            if request:
                res['extraImages'] = [request.build_absolute_uri(f'/media/{image}') for image in images]
            else:
                res['extraImages'] = [f'/media/{image}' for image in images]

        return res
    
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        
        value = value.strip()
        
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        
        return value.title()
    
    def validate_category(self, value):
        if not value or not isinstance(value, list):
            raise serializers.ValidationError("Category must be a list of category IDs.")
        
        if len(value) == 0:
            raise serializers.ValidationError("At least one category is required.")
        
        for category_id in value:
            if not isinstance(category_id, int):
                raise serializers.ValidationError("Category ID must be an integer.")
            
            if not Category.objects.filter(id=category_id).exists():
                raise serializers.ValidationError(f"Category with ID {category_id} does not exist.")
        
        return value
    
    def validate_tags(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list of tag IDs.")
        
        for tag_id in value:
            if not isinstance(tag_id, int):
                raise serializers.ValidationError("Tag ID must be an integer.")
            
            if not EventTag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(f"Tag with ID {tag_id} does not exist.")
        
        return value

    def validate_slug(self, value):
        if not value or not value.strip():
            return None
        
        value = value.lower().strip()
        
        if len(value) < 3:
            raise serializers.ValidationError("Slug must be at least 3 characters long.")
        
        import re
        if not re.match(r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$', value):
            raise serializers.ValidationError("Slug can only contain lowercase letters, numbers, and hyphens. It must start and end with alphanumeric characters.")
        
        if '--' in value:
            raise serializers.ValidationError("Slug cannot contain consecutive hyphens.")
        
        if Event.objects.filter(slug=value).exists():
            raise serializers.ValidationError(f"The slug '{value}' is already taken. Please use a different slug.")
        
        return value

    def validate_extraImages(self, value):
        if not value or len(value) == 0:
            return value
        
        allowed_extensions = ['png', 'svg', 'jpg', 'jpeg']
        max_size= 5* 1024 * 1024
        
        for image in value:
            file_ext = os.path.splitext(image.name)[1].lower().lstrip('.')
            if file_ext not in allowed_extensions:
                raise serializers.ValidationError(
                    f"Invalid file type '{file_ext}' for '{image.name}'. Allowed types: png, svg, jpg, jpeg."
                )
            
            if image.size > max_size:
                size_mb = image.size / (1024 * 1024)
                raise serializers.ValidationError(
                    f"Image Size is {size_mb:.2f}MB. Maximum file size is 5MB."
                )
        
        return value

    def validate_feature_image(self, value):
        allowed_extensions = ['png', 'svg', 'jpg', 'jpeg']
        max_size= 5 * 1024 * 1024
        
        file_ext = os.path.splitext(value.name)[1].lower().lstrip('.')
        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Invalid file type '{file_ext}'. Allowed types: png, svg, jpg, jpeg."
            )
        
        if value.size > max_size:
            size_mb = value.size / (1024 * 1024)
            raise serializers.ValidationError(
                f"Image size is {size_mb:.2f}MB. Maximum file size is 5MB."
            )
        
        return value

    def validate_short_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Short description cannot be empty.")
        
        if len(value) > 255:
            raise serializers.ValidationError("Short description cannot exceed 255 characters.")
        
        return value.strip()

    def validate_long_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Long description cannot be empty.")
                
        if len(value) < 20:
            raise serializers.ValidationError("Long description must be at least 20 characters long.")
        
        return value.strip()

    def create(self, validated_data):
        try:
            category_ids = validated_data.pop('category', [])
            tag_ids = getattr(self, 'tags_data', [])
            images_data = getattr(self, 'images_data', [])
            
            if not validated_data.get('feature_image'):
                raise serializers.ValidationError({"feature_image": "Feature image is required when creating an event."})
            
            slug = validated_data.pop('slug', None)
            if not slug or slug is None:
                title = validated_data.get('title', '')
                slug = slugify(title)
                
                base_slug = slug
                counter = 1
                while Event.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
            
            validated_data['slug'] = slug
            
            if not category_ids:
                raise serializers.ValidationError("At least one category is required.")
            
            categories = Category.objects.filter(id__in=category_ids)
            if len(categories) != len(category_ids):
                raise serializers.ValidationError("One or more category IDs do not exist.")
            
            tags = EventTag.objects.filter(id__in=tag_ids) if tag_ids else []
            
            country_id = validated_data.pop('country')
            state_id = validated_data.pop('state')
            city_id = validated_data.pop('city')
            
            country = Country.objects.get(id=country_id)
            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)
            
            validated_data['country'] = country
            validated_data['state'] = state
            validated_data['city'] = city
            
            images = []
            if isinstance(images_data, list):
                for image in images_data:
                    if image:
                        event_image = EventImages.objects.create(image=image)
                        images.append(event_image)
            
            event = Event.objects.create(**validated_data)
            
            event.category.set(categories)
            event.tags.set(tags)
            if images:
                event.extraImages.set(images)
            
            return event
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError(f"Error creating event: {str(e)}")

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        
        if 'slug' in validated_data and validated_data['slug']:
            new_slug = validated_data['slug']
            if new_slug != instance.slug and Event.objects.filter(slug=new_slug).exists():
                raise serializers.ValidationError({'slug': f"A slug '{new_slug}' already exists."})
            instance.slug = new_slug
        else:
            title = validated_data.get('title', instance.title)
            instance.slug = slugify(title)
        
        validated_data.pop('slug', None)
        
        if getattr(self, 'remove_feature_image_flag', False):
            if instance.feature_image:
                instance.feature_image.delete(save=False)
            instance.feature_image = None

        if 'feature_image' in validated_data:
            instance.feature_image = validated_data.get('feature_image')

        for img_url in getattr(self, 'remove_extra_image_paths', []):
            if not img_url:
                continue
            rel_path = img_url.split('/media/', 1)[1] if '/media/' in img_url else img_url
            try:
                img_obj = EventImages.objects.get(image=rel_path)
                instance.extraImages.remove(img_obj)
                img_obj.image.delete(save=False)
                img_obj.delete()
            except EventImages.DoesNotExist:
                pass

        if 'category' in validated_data:
            category_ids = validated_data.get('category')
            categories = Category.objects.filter(id__in=category_ids)
            if len(categories) != len(category_ids):
                raise serializers.ValidationError("One or more category IDs do not exist.")
            instance.category.set(categories)
        
        if hasattr(self, 'tags_data') and self.tags_data:
            tag_ids = self.tags_data
            tags = EventTag.objects.filter(id__in=tag_ids)
            instance.tags.set(tags)
        
        if hasattr(self, 'images_data') and self.images_data:
            images_data = self.images_data
            if isinstance(images_data, list):
                for image in images_data:
                    if image:
                        event_image = EventImages.objects.create(image=image)
                        instance.extraImages.add(event_image)
        
        if 'country' in validated_data:
            country_id = validated_data.get('country')
            instance.country = Country.objects.get(id=country_id)
        
        if 'state' in validated_data:
            state_id = validated_data.get('state')
            instance.state = State.objects.get(id=state_id)
        
        if 'city' in validated_data:
            city_id = validated_data.get('city')
            instance.city = City.objects.get(id=city_id)
        
        instance.venue = validated_data.get('venue', instance.venue)
        instance.event_date = validated_data.get('event_date', instance.event_date)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.long_description = validated_data.get('long_description', instance.long_description)
        instance.save()
        return instance
