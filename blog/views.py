from rest_framework import status, viewsets, permissions
from rest_framework.views import APIView
from .serializers import PostSerializer, CategorySerializer, CommentSerializer
from rest_framework.response import Response
from .models import Post, Category, Comment
from django.http import HttpResponse
from django.http import Http404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, BasePermission, SAFE_METHODS, AllowAny, IsAdminUser, DjangoModelPermissions
from rest_framework.serializers import CurrentUserDefault
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticatedOrReadOnly]


    def perform_create(self, serializer):
        if self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser):
            serializer.save(author=self.request.user)
        else:
            raise PermissionDenied("You do not have permission to create a post.")


    def perform_update(self, serializer):
        instance = self.get_object()
        if self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser or instance.author == self.request.user):
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to update this post.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this post.")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        queryset = Comment.objects.filter(post_id=post_id)
        return queryset


    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(post=post, user=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser or instance.author == self.request.user):
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to update this post.")
