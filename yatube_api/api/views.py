from django.shortcuts import get_object_or_404
from posts.models import Group, Post
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Создаём вьюсет для группы"""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PostViewSet(viewsets.ModelViewSet):
    """Создаём вьюсет для постов
    авторизованных пользователей"""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnlyPermission]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """Пропишем создание и сохранение нового поста"""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Пропишем обновление и сохранение поста"""
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """Создаём вьюсет для комментариев
    Комментировать могу авторизованные пользователи"""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnlyPermission]

    def perform_create(self, serializer):
        """Пропишем создание нового комментария
        к публикации автором поста, для этого
        найдём пост по его id и сохраним коммент
        авторизованного пользователя.Анонимные запросы запрещены."""

        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)

    def get_queryset(self):
        """Получим список комментариев по id поста"""

        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        return post.comments.all()


class CreateListViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Создадим класс, позволящий пользователю
    просматривать своих подписчиков и подписываться
    на новых авторов."""
    pass


class FollowViewSet(CreateListViewSet):
    """Создаём вьюсет для подписок и подписчиков.
    Доступен только авторизованным пользователям."""

    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
