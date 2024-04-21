from django.urls import path
from .views import UserRegistrationView, UserVerificationView, UserLoginView, LoginVerificationView, check_auth

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('verify/', UserVerificationView.as_view(), name='user_verification'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('login/verify/', LoginVerificationView.as_view(), name='login_verification'),
    path('check-auth/', check_auth, name='check-auth'),


]
