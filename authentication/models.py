from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


# User Types
USER_TYPE_CHOICES = (
    ('organizer', 'Event Organizer'),
    ('vendor', 'Vendor'),
    ('admin', 'Admin'),
     ('guest', 'Guest'),
)

# Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, user_type='organizer', password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, user_type='admin', password=password, **extra_fields)


# Custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='guest')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Organizer paystack info.
    subaccount_code = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_code = models.CharField(max_length=10, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
