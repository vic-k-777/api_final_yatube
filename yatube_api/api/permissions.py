from rest_framework import permissions


class IsAuthorOrReadOnlyPermission(permissions.BasePermission):
    """Создаём пермишен, который не даст пользователю удалить
    или отредактировать чужие публикации. Запрашивать список
    всех публикаций или отдельную публикацию может любой пользователь.
    Создавать новую публикацию может только
    аутентифицированный пользователь."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True
        return request.method in permissions.SAFE_METHODS
