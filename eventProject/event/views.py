from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound
from .serializers import UserSerializer, CategorySerializer, EventTagSerializer, EventSerializer, LoginSerializer, RefreshTokenSerializer
from .models import Category, EventTag, Event


class SignUpViewset(viewsets.ViewSet):
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = serializer.get_tokens(user)
            return Response(
                {
                    'message': 'Login successful',
                    'tokens': tokens
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenViewSet(viewsets.ViewSet):
    
    def create(self, request):

        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                tokens = serializer.new_access_token(serializer.validated_data['refresh'])
                return Response(
                    {
                        'message': 'New Access Token: ',
                        'tokens': tokens
                    },
                    status=status.HTTP_200_OK
                )
            except serializer.ValidationError as e:
                return Response({'error': str(e.detail[0])}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def create(self, request):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can create events.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can create events.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can update categories.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can create events.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


class EventTagViewSet(viewsets.ViewSet): 
    permission_classes = [AllowAny]

    def list(self, request):
        tags = EventTag.objects.all()
        serializer = EventTagSerializer(tags, many=True)
        return Response(serializer.data)

    def create(self, request):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can create tags.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = EventTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            tag = EventTag.objects.get(pk=pk)
            serializer = EventTagSerializer(tag)
            return Response(serializer.data)
        except EventTag.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can update tags.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            tag = EventTag.objects.get(pk=pk)
            serializer = EventTagSerializer(tag, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except EventTag.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can update tags.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            tag = EventTag.objects.get(pk=pk)
            serializer = EventTagSerializer(tag, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except EventTag.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can delete tags.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            tag = EventTag.objects.get(pk=pk)
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except EventTag.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


class EventViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    
    def get_object(self, slug=None):
        try:
            return Event.objects.get(slug=slug)
        except Event.DoesNotExist:
            raise NotFound({'detail': 'Event not found.'})
    
    def list(self, request):
        events = Event.objects.all()
        
        search = request.query_params.get('search', None)
        if search:
            events = events.filter(
                Q(title__icontains=search) |
                Q(category__name__icontains=search) |
                Q(tags__name__icontains=search) |
                Q(slug__icontains=search)
            )
        
        title = request.query_params.get('title', None)
        if title:
            events = events.filter(title__icontains=title)
        
        category = request.query_params.get('category', None)
        if category:
            events = events.filter(category__name__icontains=category)
        

        tag = request.query_params.get('tag', None)
        if tag:
            events = events.filter(tags__name__icontains=tag)
        
        slug = request.query_params.get('slug', None)
        if slug:
            events = events.filter(slug__icontains=slug)
        
        status_filter = request.query_params.get('status', None)
        if status_filter is not None:
            status_filter = status_filter.lower() in ['true', '1', 'yes', 'active']
            events = events.filter(is_active=status_filter)
        
        
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can create events.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, slug=None):
        event = self.get_object(slug)
        event.views_count +=1
        event.save()

        # Event.objects.filter(slug=slug).update(views_count=F('views_count') + 1)
        
        # event.refresh_from_db()
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data)

    def update(self, request, slug=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can update events.'},
                status=status.HTTP_403_FORBIDDEN
            )
        event = self.get_object(slug)
        serializer = EventSerializer(event, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, slug=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can update events.'},
                status=status.HTTP_403_FORBIDDEN
            )
        event = self.get_object(slug)
        serializer = EventSerializer(event, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, slug=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can delete events.'},
                status=status.HTTP_403_FORBIDDEN
            )
        event = self.get_object(slug)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EventListView(View):
    def get(self, request):
        events = Event.objects.filter(is_active=True).order_by('event_date')
        context = {'events': events}
        return render(request, 'event/events_list.html', context)


class EventDetailView(View):
    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug, is_active=True)
        event.views_count += 1
        event.save()
        context = {'event': event}
        return render(request, 'event/event_detail.html', context)