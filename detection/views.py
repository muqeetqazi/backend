from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from .models import DetectionModel, DetectionJob
from .serializers import (
    DetectionModelSerializer,
    DetectionJobSerializer,
    AnalyzeDocumentSerializer,
    DetectionResultSerializer,
    MLAnalysisPayloadSerializer
)
from .detection_service import DetectionService


class DetectionModelViewSet(mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """
    ViewSet for ML detection models
    """
    queryset = DetectionModel.objects.filter(active=True)
    serializer_class = DetectionModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['model_type']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class DetectionJobViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    ViewSet for detection jobs
    """
    serializer_class = DetectionJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'document']
    ordering_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']
    
    def get_queryset(self):
        """
        Filter jobs to return only those related to the current user's documents
        """
        return DetectionJob.objects.filter(document__user=self.request.user)


class AnalysisViewSet(viewsets.ViewSet):
    """
    ViewSet for document analysis
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request):
        """
        Analyze a document for sensitive information
        """
        # Check if this is an ML model payload
        if 'source' in request.data and request.data['source'] == 'ml_model':
            return self._handle_ml_payload(request)
        else:
            return self._handle_backend_analysis(request)
    
    def _handle_ml_payload(self, request):
        """
        Handle ML model detection payload
        """
        serializer = MLAnalysisPayloadSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                # Create analysis result from ML payload
                scan = serializer.create_ml_analysis_result(serializer.validated_data)
                
                # Update user statistics using F() expressions
                user = request.user
                sensitive_count = serializer.validated_data['sensitive_items_count']
                
                if sensitive_count > 0:
                    user.total_sensitive_items_detected = F('total_sensitive_items_detected') + sensitive_count
                    user.save(update_fields=["total_sensitive_items_detected"])
                else:
                    user.total_non_detected_items = F('total_non_detected_items') + 1
                    user.save(update_fields=["total_non_detected_items"])
                
                # Log the ML detection stats
                print(f"✅ ML detection stats recorded: document_id={scan.document.id}, sensitive_items_count={sensitive_count}")
                
                # Return success acknowledgment
                response_data = {
                    'document_id': scan.document.id,
                    'scan_id': scan.id,
                    'scan_date': scan.scan_date.isoformat(),
                    'sensitive_items_count': sensitive_count,
                    'source': 'ml_model',
                    'status': 'recorded'
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response(
                    {'error': f'Failed to process ML payload: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_backend_analysis(self, request):
        """
        Handle backend document analysis (original logic)
        """
        serializer = AnalyzeDocumentSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            document_id = serializer.validated_data['document_id']
            
            # Call the detection service
            detection_service = DetectionService()
            results = detection_service.analyze_document(document_id)
            
            # Check for error
            if 'error' in results:
                return Response(
                    {'error': results['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create DocumentScan and SensitiveInformation records
            result_serializer = DetectionResultSerializer(data=results)
            if result_serializer.is_valid():
                scan = result_serializer.save()
                
                # Track sensitive items detected using F() expressions for atomic updates
                user = request.user
                sensitive_count = scan.sensitive_information.count()
                
                if sensitive_count > 0:
                    # Increment sensitive items detected counter
                    user.total_sensitive_items_detected = F('total_sensitive_items_detected') + sensitive_count
                    user.save(update_fields=["total_sensitive_items_detected"])
                    print(f"✅ Found {sensitive_count} sensitive items for user {user.id}")
                else:
                    # If no sensitive items detected, increment non-detected counter
                    user.total_non_detected_items = F('total_non_detected_items') + 1
                    user.save(update_fields=["total_non_detected_items"])
                    print(f"ℹ️ No sensitive items found for user {user.id}")
                
                # Return the scan results
                response_data = {
                    'scan_id': scan.id,
                    'document_id': scan.document.id,
                    'risk_level': scan.risk_level,
                    'processing_time': scan.processing_time,
                    'scan_date': scan.scan_date,
                    'sensitive_items_count': sensitive_count,
                    'sensitive_items': [
                        {
                            'type': si.type,
                            'type_display': si.get_type_display(),
                            'confidence': si.confidence,
                            'location': si.location,
                            'count': si.count,
                            'redacted': si.redacted
                        }
                        for si in scan.sensitive_information.all()
                    ]
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    result_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 