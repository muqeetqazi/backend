from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model for the Protected Vision app
    """
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    
    # User activity tracking fields
    total_documents_saved = models.PositiveIntegerField(default=0, help_text="Total documents uploaded/saved")
    total_documents_processed = models.PositiveIntegerField(default=0, help_text="Total documents processed")
    total_documents_shared = models.PositiveIntegerField(default=0, help_text="Total documents shared")
    total_sensitive_items_detected = models.PositiveIntegerField(default=0, help_text="Total sensitive items found")
    total_non_detected_items = models.PositiveIntegerField(default=0, help_text="Total items that were not detected as sensitive")
    
    # Override the username field to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
    def get_detection_accuracy(self):
        """
        Calculate detection accuracy percentage
        """
        total_items = self.total_sensitive_items_detected + self.total_non_detected_items
        if total_items == 0:
            return 0
        return (self.total_sensitive_items_detected / total_items) * 100
    
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