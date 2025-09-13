from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Document(models.Model):
    """
    Model to store uploaded documents
    """
    TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('pdf', 'PDF Document'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    file_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")


class DocumentScan(models.Model):
    """
    Model to store document scan results
    """
    RISK_LEVEL_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='scans')
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default='low')
    processed_file = models.FileField(upload_to='processed_documents/%Y/%m/%d/', null=True, blank=True)
    processing_time = models.FloatField(help_text="Processing time in seconds")
    scan_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Scan for {self.document.title} - {self.risk_level} risk"
    
    class Meta:
        ordering = ['-scan_date']
        verbose_name = _("Document Scan")
        verbose_name_plural = _("Document Scans")


class SensitiveInformation(models.Model):
    """
    Model to store detected sensitive information
    """
    TYPE_CHOICES = (
        ('pii', 'Personal Identifiable Information'),
        ('credit_card', 'Credit Card'),
        ('passport', 'Passport'),
        ('driver_license', 'Driver License'),
        ('bank_account', 'Bank Account'),
        ('social_security', 'Social Security Number'),
        ('phone_number', 'Phone Number'),
        ('email', 'Email Address'),
        ('address', 'Physical Address'),
        ('medical_record', 'Medical Record'),
        ('other', 'Other'),
    )
    
    scan = models.ForeignKey(DocumentScan, on_delete=models.CASCADE, related_name='sensitive_information')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    confidence = models.FloatField(help_text="Confidence score (0-1)")
    location = models.JSONField(null=True, blank=True, help_text="Coordinates in document [x, y, width, height]")
    count = models.PositiveIntegerField(default=1, help_text="Number of instances found")
    redacted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_type_display()} in {self.scan.document.title}"
    
    class Meta:
        verbose_name = _("Sensitive Information")
        verbose_name_plural = _("Sensitive Information") 