

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, firstname,lastname, password,phoneno,**kwargs):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)

        user = self.model(email=email,firstname=firstname,lastname=lastname,phoneno=phoneno,**kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, firstname,lastname, password, phoneno, **kwargs):
        user = self.create_user(email, firstname,lastname, password,phoneno,**kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=255, unique=True)
    firstname = models.CharField(max_length=255,blank=True,null=True)
    lastname = models.CharField(max_length=255,blank=True,null=True)
    phoneno = models.CharField(max_length=10)
    otp = models.IntegerField(blank=True,null=True)
    expiry_otp=models.DateTimeField(blank=True, null=True)

    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_address = models.TextField(blank=True, null=True)
    company_pan_number = models.CharField(max_length=10, blank=True, null=True)



    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'



    objects = CustomUserManager()

    groups = models.ManyToManyField(Group, related_name='customUser_group_set',blank=True)

    user_permissions = models.ManyToManyField(Permission,related_name='customUser_permission_set',blank=True)

    def __str__(self):
        return self.email





