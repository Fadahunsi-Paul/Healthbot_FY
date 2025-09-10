from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .usermanager import UserManager
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

# Create your models here.


class User(AbstractUser):
    username = None
    email = models.EmailField(_("Email Address"), unique=True)
    first_name = models.CharField(_("First Name"), max_length=150)
    last_name = models.CharField(_("Last Name"), max_length=150)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="auth_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="auth_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]  # Required for creating superuser

    objects = UserManager()

    def __str__(self):
        return self.email if self.email else ""

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)
    
    # Health Information
    medical_conditions = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    blood_type = models.CharField(max_length=5, blank=True, null=True)
    height = models.CharField(max_length=10, blank=True, null=True)  # in cm
    weight = models.CharField(max_length=10, blank=True, null=True)  # in kg
    
    # Settings
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    health_reminders = models.BooleanField(default=True)
    appointment_reminders = models.BooleanField(default=True)
    
    # Privacy Settings
    share_health_data = models.BooleanField(default=False)
    allow_analytics = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Profile for {self.user.email}'

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class ResetPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6,null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Code {self.code} generated for {self.user}'

    def is_valid(self):
        return timezone.now() < self.created_at + timezone.timedelta(minutes=5)