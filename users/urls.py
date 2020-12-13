from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import UserCreate, HelloWorldView

urlpatterns = [
    path('user/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('auth/register/', UserCreate.as_view(), name="create_user"),
    path('auth/login/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('auth/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
