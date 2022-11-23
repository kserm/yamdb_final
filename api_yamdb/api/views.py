from api.customs_viewsets import CategoryGenreBasicViewSet
from api.filters import TitlesFilter
from api.permissions import (IsAdmin, IsAdminOrReadOnly,
                             IsAuthorModeratorAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignUpSerializer, TitlesSerializerReceive,
                             TitlesSerializerSend, TokenSerializer,
                             UserSerializer)
from api.utils import send_mail_function
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title
from users.models import User


@api_view(["POST"])
def register_user(request):
    """Регистрация нового пользователя """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = serializer.instance
    confirmation_code = default_token_generator.make_token(user)
    send_mail_function(user, confirmation_code)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_token_for_users(request):
    """Получить токен"""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    refresh = RefreshToken.for_user(
        serializer.validated_data["username"]
    )
    return Response(
        {"refresh": str(refresh)},
        status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    """Логика работы с пользователями"""
    queryset = User.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    permission_classes = (IsAdmin,)
    serializer_class = UserSerializer

    @action(
        methods=["GET", "PATCH"],
        permission_classes=(IsAuthenticated,),
        url_path="me", detail=False)
    def users_profile(self, request):
        if request.method == "PATCH":
            serializer = self.serializer_class(
                request.user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data["role"] = request.user.role
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK)
        # Если GET запрос, возвращаем страницу пользователя
        serializer = self.serializer_class(request.user)
        return Response(
            serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(CategoryGenreBasicViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBasicViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitlesViewSet(ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return TitlesSerializerSend
        return TitlesSerializerReceive


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthorModeratorAdminOrReadOnly,
        IsAuthenticatedOrReadOnly
    ]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs["title_id"])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title())


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthorModeratorAdminOrReadOnly,
        IsAuthenticatedOrReadOnly
    ]

    def get_review(self):
        return get_object_or_404(
            Review, id=self.kwargs["review_id"],
            title__id=self.kwargs["title_id"]
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review())
