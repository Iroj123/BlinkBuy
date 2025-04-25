from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import  permissions, status

from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import CustomUser
from authentication.serializers import RegistrationSerializer, LoginSerializer, OtpSerializer, ForgetPasswordSerializer, \
    ResetPasswordSerializer, OtpValidationForResetSerializer, ChangePasswordSerializer, VendorRegistrationSerializer


class RegisterView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            return Response({'message': 'User registered. Please check your email for OTP.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class VerifyEmailView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = OtpSerializer

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = CustomUser.objects.get(email=email, otp=otp)

            user.verify_otp()

            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid code or email"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response({'error': 'Missing username or password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)

        if user is None:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_verified:
            return Response({"error": "Email is not verified. Please check your email for the verification code."},
                            status=status.HTTP_403_FORBIDDEN)

            # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'message': 'User logged in successfully.',
            'access_token': access_token,
            'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)


class ForgetPasswordView(GenericAPIView):
    serializer_class = ForgetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Generates OTP inside serializer
            return Response({"message": "OTP sent to email for password reset."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(GenericAPIView):

    serializer_class = OtpValidationForResetSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            try:
                user = CustomUser.objects.get(email=email, otp=otp)
                request.session['otp_verified'] = True
                user.verify_otp()

                return Response({"message": "OTP verified. You may now reset your password."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "Invalid email or OTP."}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(GenericAPIView):

    serializer_class = ResetPasswordSerializer
    permission_classes = (permissions.AllowAny,)


    def post(self, request, *args, **kwargs):

        if not request.session.get('otp_verified'):
            return Response({"error": "OTP not verified. Please verify OTP before resetting the password."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            del request.session['otp_verified']
            return Response({"message": "Password reset successful. You can now log in with your new password."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ChangePasswordView(GenericAPIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        # Use the serializer to validate and change the password
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VendorRegisterView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    serializer_class = VendorRegistrationSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            vendor_group, created = Group.objects.get_or_create(name='Vendor')
            user.groups.add(vendor_group)
            return Response({'message': 'User registered. Please check your email for OTP.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)




