from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import VerifyEmailView, LoginView, RegisterView, ForgetPasswordView, VerifyOtpView, \
    ResetPasswordView, ChangePasswordView

urlpatterns = [
path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify/', VerifyEmailView.as_view(), name='login'),
    path('password-forget/', ForgetPasswordView.as_view(), name='password-forget'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]