from django.urls import path
from .views import RegisterView, LoginView, UserProfileView, UserListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ForgotPasswordView, ResetPasswordView, preview_reset_email
from .views import SetupSubaccountView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user_list'), 
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('preview-reset-email/', preview_reset_email, name='preview-reset-email'),
    path('organizer/setup-subaccount/', SetupSubaccountView.as_view(), name='setup-subaccount'),

]
