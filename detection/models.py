from django.db import models
from django.utils.translation import gettext_lazy as _
from documents.models import Document


class DetectionModel(models.Model):
    """
    Model to store information about trained detection models
    """
    TYPE_CHOICES = (
        ('yolo', 'YOLO - Object Detection'),
        ('ocr', 'OCR - Text Recognition'),
        ('transformer', 'Transformer - NLP'),
    )
    
    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    version = models.CharField(max_length=50)
    weights_file = models.FileField(upload_to='detection_models/', blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - v{self.version}"
    
    class Meta:
        verbose_name = _("Detection Model")
        verbose_name_plural = _("Detection Models")


class DetectionJob(models.Model):
    """
    Model to store detection job status and metadata
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='detection_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    models_used = models.ManyToManyField(DetectionModel, related_name='jobs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Detection job for {self.document.title} - {self.status}"
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = _("Detection Job")
        verbose_name_plural = _("Detection Jobs") 