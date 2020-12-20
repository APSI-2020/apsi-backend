from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import UserCreate, HelloWorldView, UserGroupsView, LecturersView

urlpatterns = [
    path('user/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('user/user-groups/', UserGroupsView.as_view(), name='get_user_groups'),
    path('user/lecturers/', LecturersView.as_view(), name='get_lecturers'),
    path('auth/register/', UserCreate.as_view(), name="create_user"),
    path('auth/login/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('auth/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
