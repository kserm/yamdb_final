from api.permissions import IsAdminOrReadOnly
from rest_framework import mixins
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import GenericViewSet


class CategoryGenreBasicViewSet(GenericViewSet, mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                mixins.DestroyModelMixin):
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    permission_classes = (IsAdminOrReadOnly,)
