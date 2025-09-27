from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, DocumentScan
from .serializers import (
    DocumentSerializer,
    DocumentWithScansSerializer,
    DocumentScanSerializer
)
from users.services.stats import UserStatsService


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for documents - allows CRUD operations
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['file_type', 'processed']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter documents to return only those belonging to the current user
        """
        # Handle schema generation for Swagger docs
        if getattr(self, 'swagger_fake_view', False):
            return Document.objects.none()
        
        # Only return documents for authenticated users
        if self.request.user.is_authenticated:
            return Document.objects.filter(user=self.request.user)
        return Document.objects.none()
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action
        """
        if self.action == 'retrieve':
            return DocumentWithScansSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """
        Override to track document upload
        """
        document = serializer.save(user=self.request.user)
        # Increment documents saved counter
        UserStatsService.increment_documents_saved(self.request.user)
    
    def perform_update(self, serializer):
        """
        Override to track document processing
        """
        # Get the current state before update
        old_processed = self.get_object().processed
        
        # Save the document with new data
        document = serializer.save()
        
        # Check if processed status changed from False to True
        if not old_processed and document.processed:
            # Increment the documents processed counter
            UserStatsService.increment_documents_processed(self.request.user)
            print(f"✅ Document {document.id} marked as processed for user {self.request.user.id}")
        elif old_processed and not document.processed:
            print(f"⚠️ Document {document.id} marked as unprocessed for user {self.request.user.id}")
        else:
            print(f"ℹ️ Document {document.id} processed status unchanged: {document.processed}")
    
    @action(detail=True, methods=['get'])
    def scans(self, request, pk=None):
        """
        Return all scans for a specific document
        """
        document = self.get_object()
        scans = document.scans.all()
        serializer = DocumentScanSerializer(scans, many=True)
        return Response(serializer.data)


class DocumentScanViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    ViewSet for document scans - read-only operations
    """
    serializer_class = DocumentScanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['risk_level']
    ordering_fields = ['scan_date']
    ordering = ['-scan_date']
    
    def get_queryset(self):
        """
        Filter scans to return only those related to the current user's documents
        """
        # Handle schema generation for Swagger docs
        if getattr(self, 'swagger_fake_view', False):
            return DocumentScan.objects.none()
        
        # Only return scans for authenticated users
        if self.request.user.is_authenticated:
            return DocumentScan.objects.filter(document__user=self.request.user)
        return DocumentScan.objects.none() 