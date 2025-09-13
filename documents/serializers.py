from rest_framework import serializers
from .models import Document, DocumentScan, SensitiveInformation


class SensitiveInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for sensitive information detected in documents
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = SensitiveInformation
        fields = [
            'id', 
            'type', 
            'type_display', 
            'confidence', 
            'location', 
            'count', 
            'redacted'
        ]


class DocumentScanSerializer(serializers.ModelSerializer):
    """
    Serializer for document scan results
    """
    sensitive_information = SensitiveInformationSerializer(many=True, read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    
    class Meta:
        model = DocumentScan
        fields = [
            'id', 
            'document', 
            'risk_level', 
            'risk_level_display', 
            'processed_file', 
            'processing_time',
            'scan_date', 
            'sensitive_information'
        ]
        read_only_fields = ['document', 'scan_date']


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for document uploads and metadata
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 
            'user', 
            'title', 
            'file', 
            'file_type', 
            'file_type_display', 
            'processed',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['processed', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the user to the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DocumentWithScansSerializer(DocumentSerializer):
    """
    Detailed document serializer that includes scan results
    """
    scans = DocumentScanSerializer(many=True, read_only=True)
    
    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ['scans'] 