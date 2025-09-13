from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model for the Protected Vision app
    """
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    
    # Override the username field to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class UserPreference(models.Model):
    """
    User preferences for the application
    """
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System Default'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    dark_mode = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='system')
    auto_delete_processed_files = models.BooleanField(default=False)
    auto_delete_after_days = models.PositiveIntegerField(default=30)
    
    def __str__(self):
        return f"{self.user.email}'s preferences"
    
    class Meta:
        verbose_name = _("User Preference")
        verbose_name_plural = _("User Preferences") 