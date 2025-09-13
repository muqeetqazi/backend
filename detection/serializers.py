from rest_framework import serializers
from .models import DetectionModel, DetectionJob
from documents.models import Document, DocumentScan, SensitiveInformation


class DetectionModelSerializer(serializers.ModelSerializer):
    """
    Serializer for ML models used for detection
    """
    model_type_display = serializers.CharField(source='get_model_type_display', read_only=True)
    
    class Meta:
        model = DetectionModel
        fields = [
            'id', 
            'name', 
            'model_type', 
            'model_type_display', 
            'version', 
            'active', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DetectionJobSerializer(serializers.ModelSerializer):
    """
    Serializer for detection jobs
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    models_used = DetectionModelSerializer(many=True, read_only=True)
    
    class Meta:
        model = DetectionJob
        fields = [
            'id', 
            'document', 
            'status', 
            'status_display', 
            'models_used', 
            'started_at', 
            'completed_at', 
            'error_message'
        ]
        read_only_fields = ['status', 'models_used', 'started_at', 'completed_at', 'error_message']


class AnalyzeDocumentSerializer(serializers.Serializer):
    """
    Serializer for document analysis request
    """
    document_id = serializers.IntegerField()
    
    def validate_document_id(self, value):
        try:
            document = Document.objects.get(id=value)
            # Check if the document belongs to the current user
            if document.user != self.context['request'].user:
                raise serializers.ValidationError("You don't have permission to analyze this document")
            return value
        except Document.DoesNotExist:
            raise serializers.ValidationError("Document not found")


class SensitiveItemSerializer(serializers.Serializer):
    """
    Serializer for sensitive information items
    """
    type = serializers.CharField()
    confidence = serializers.FloatField()
    location = serializers.JSONField(required=False)
    count = serializers.IntegerField(default=1)


class DetectionResultSerializer(serializers.Serializer):
    """
    Serializer for detection results
    """
    document_id = serializers.IntegerField()
    risk_level = serializers.ChoiceField(choices=['low', 'medium', 'high'])
    processing_time = serializers.FloatField()
    sensitive_items = SensitiveItemSerializer(many=True)
    
    def create(self, validated_data):
        """
        Create DocumentScan and SensitiveInformation records
        """
        document_id = validated_data.pop('document_id')
        sensitive_items = validated_data.pop('sensitive_items')
        
        # Get the document
        document = Document.objects.get(id=document_id)
        
        # Create the scan record
        scan = DocumentScan.objects.create(
            document=document,
            **validated_data
        )
        
        # Create sensitive information records
        for item in sensitive_items:
            SensitiveInformation.objects.create(
                scan=scan,
                **item
            )
        
        # Mark the document as processed
        document.processed = True
        document.save()
        
        return scan 