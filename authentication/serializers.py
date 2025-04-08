from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from rest_framework import serializers

from authentication.models import CustomUser


def send_otp(self):
    from django.core.mail import send_mail
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {self.otp}.',
        'EMAIL_HOST_USER',
        [self.email],
        fail_silently=False,
    )



class RegistrationSerializer(serializers.ModelSerializer):

    password=serializers.CharField(write_only=True)
    re_password=serializers.CharField(write_only=True)
    class Meta:
        model=CustomUser
        fields= ['email','firstname','lastname','phoneno','password','re_password']
        extra_kwargs = {
            'password': {'required': True},
            're_password': {'required': True},
        }
    def validate_email(self, value):

        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate(self,data):
        password=data.get('password')
        re_password=data.get('re_password')
        if password != re_password:
            raise serializers.ValidationError('Passwords do not match')
        return data





    def create(self, validated_data):
        validated_data.pop('re_password',None)
        user=get_user_model().objects.create_user( email=validated_data['email'],
        firstname=validated_data['firstname'],
        lastname=validated_data['lastname'],
        phoneno=validated_data['phoneno'],
        password=validated_data['password'])

        user.is_verified = False
        user.otp = get_random_string(length=6, allowed_chars="0123456789")
        user.expiry_otp = datetime.now() + timedelta(minutes=5)
        user.save()
        send_otp(user)
        return user


class OtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data["email"]
        otp = data["otp"]
        # Check if the OTP matches the one stored in the database
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        if user.expiry_otp and user.expiry_otp < now():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")



        return data


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['email','password']


    def validate(self,data):
        email=data.get('email')
        password=data.get('password')

        if email == None or password == None:
            raise serializers.ValidationError('Email and password are required.')

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist.')

        if not user.check_password(password):
            raise serializers.ValidationError('Passwords do not match')

        return user






class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)

        # Generate new OTP for password reset
        user.otp = get_random_string(length=6, allowed_chars="0123456789")
        user.expiry_otp = datetime.now() + timedelta(minutes=5)


        user.save()

        # Send OTP email
        send_otp(user)
        return {"message": "OTP sent to email for password reset."}



class OtpValidationForResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp= serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        otp = data['otp']

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if int(user.otp) != int(otp):
            raise serializers.ValidationError("Invalid OTP.")

        if user.expiry_otp and user.expiry_otp < now():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        return data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    re_enter_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        email = data["email"]
        new_password = data['new_password']
        confirm_password = data['re_enter_password']

        try:
            user = CustomUser.objects.get(email=email)

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if new_password != confirm_password:
            raise serializers.ValidationError('Passwords do not match')

        return data

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']

        user = CustomUser.objects.get(email=email)
        user.set_password(new_password)
        user.save()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)
    re_enter_password = serializers.CharField(write_only=True, min_length=6)


    def validate(self, data):
        old_password = data['old_password']
        new_password = data['new_password']
        confirm_password = data['re_enter_password']
        if new_password != confirm_password:
            raise serializers.ValidationError('Passwords do not match')

        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError("Current password is incorrect.")

        return data

    def save(self):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()





class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'firstname','lastname','phoneno','groups']



# class UserRoleUpdateSerializer(serializers.Serializer):
#     role = serializers.ChoiceField(choices=["Admin", "Vendor", "User"])
#
#     def update(self, instance, validated_data):
#         role = validated_data["role"]
#
#         # Remove from all role groups
#         role_groups = ["Admin", "Vendor", "User"]
#         for group_name in role_groups:
#             group = Group.objects.get(name=group_name)
#             instance.groups.remove(group)
#
#         # Add to the selected group
#         new_group = Group.objects.get(name=role)
#         instance.groups.add(new_group)
#
#         instance.save()
#         return instance



class VendorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email','phoneno','company_name','company_address','company_pan_number','password','re_password']
        extra_kwargs = {
            'password': {'required': True},
            're_password': {'required': True},
        }


    def validate_email(self, value):

        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate(self, data):
        password = data.get('password')
        re_password = data.get('re_password')
        if password != re_password:
            raise serializers.ValidationError('Passwords do not match')
        return data

    def create(self, validated_data):
        validated_data.pop('re_password', None)

        firstname = validated_data.get('firstname', '')
        lastname = validated_data.get('lastname', '')

        user = get_user_model().objects.create_user(email=validated_data['email'],
                                                        company_name=validated_data['company_name'],
                                                        company_address=validated_data['company_address'],
                                                        company_pan_number=validated_data['company_pan_number'],
                                                        firstname=firstname,
                                                        lastname=lastname,
                                                        phoneno=validated_data['phoneno'],
                                                        password=validated_data['password'])

        user.is_verified = False
        user.otp = get_random_string(length=6, allowed_chars="0123456789")
        user.expiry_otp = datetime.now() + timedelta(minutes=5)
        user.save()
        send_otp(user)
        return user



















