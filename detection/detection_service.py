import time
import os
import random
import cv2
import numpy as np
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw

from documents.models import Document, DocumentScan, SensitiveInformation
from .models import DetectionModel, DetectionJob


class DetectionService:
    """
    Service for detecting sensitive information in documents
    
    This is a placeholder implementation that simulates detection.
    In a real implementation, this would use actual ML models.
    """
    
    def __init__(self):
        self.yolo_weights_path = getattr(settings, 'ML_MODELS', {}).get(
            'YOLO_WEIGHTS_PATH', None
        )
        self.confidence_threshold = getattr(settings, 'ML_MODELS', {}).get(
            'CONFIDENCE_THRESHOLD', 0.5
        )
        self.iou_threshold = getattr(settings, 'ML_MODELS', {}).get(
            'IOU_THRESHOLD', 0.45
        )
    
    def analyze_document(self, document_id):
        """
        Main method to analyze a document for sensitive information
        
        Args:
            document_id (int): ID of the document to analyze
            
        Returns:
            dict: Detection results
        """
        start_time = time.time()
        
        # Get the document
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return {"error": "Document not found"}
        
        # Create a detection job
        job = DetectionJob.objects.create(
            document=document,
            status='processing'
        )
        
        try:
            # Get active detection models
            active_models = DetectionModel.objects.filter(active=True)
            job.models_used.set(active_models)
            
            # Process based on file type
            if document.file_type == 'image':
                results = self._process_image(document)
            elif document.file_type == 'video':
                results = self._process_video(document)
            elif document.file_type == 'pdf':
                results = self._process_pdf(document)
            else:
                results = {"error": "Unsupported file type"}
                job.status = 'failed'
                job.error_message = "Unsupported file type"
                job.save()
                return results
            
            # Calculate risk level based on sensitive items found
            risk_level = self._calculate_risk_level(results)
            
            # Create processed file with redactions
            processed_file = self._create_redacted_file(document, results)
            
            # Store a reference to the processed file
            if processed_file:
                # Keep track of processing time
                processing_time = time.time() - start_time
                
                # Update job status
                job.status = 'completed'
                job.completed_at = datetime.now()
                job.save()
                
                # Return results
                return {
                    "document_id": document.id,
                    "risk_level": risk_level,
                    "processing_time": processing_time,
                    "sensitive_items": results
                }
            else:
                job.status = 'failed'
                job.error_message = "Failed to create processed file"
                job.save()
                return {"error": "Failed to create processed file"}
                
        except Exception as e:
            # Update job status in case of error
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            return {"error": str(e)}
    
    def _process_image(self, document):
        """
        Process an image document to detect sensitive information
        
        This is a placeholder implementation that returns mock results.
        In a real implementation, this would use actual ML models.
        
        Args:
            document (Document): Document object to process
            
        Returns:
            list: List of detected sensitive items
        """
        # In a real implementation, this would load the image and pass it to ML models
        
        # Simulate processing delay
        time.sleep(2)
        
        # Return mock results
        mock_sensitive_types = [
            'credit_card', 'passport', 'driver_license', 'social_security',
            'phone_number', 'email', 'address', 'bank_account', 'pii'
        ]
        
        results = []
        for _ in range(random.randint(1, 5)):  # Random number of detections
            sensitive_type = random.choice(mock_sensitive_types)
            confidence = random.uniform(0.75, 0.99)
            location = {
                'x': random.randint(10, 500),
                'y': random.randint(10, 500),
                'width': random.randint(50, 200),
                'height': random.randint(20, 50)
            }
            results.append({
                'type': sensitive_type,
                'confidence': confidence,
                'location': location,
                'count': 1
            })
        
        return results
    
    def _process_video(self, document):
        """
        Process a video to detect sensitive information
        
        This is a placeholder implementation that returns mock results.
        In a real implementation, this would analyze frames from the video.
        
        Args:
            document (Document): Document object to process
            
        Returns:
            list: List of detected sensitive items
        """
        # Simulate processing delay
        time.sleep(5)
        
        # Just use the image processor as a mock
        results = self._process_image(document)
        
        # Add video-specific metadata
        for item in results:
            item['frame'] = random.randint(1, 500)
            
        return results
    
    def _process_pdf(self, document):
        """
        Process a PDF to detect sensitive information
        
        This is a placeholder implementation that returns mock results.
        In a real implementation, this would extract images and text from PDF pages.
        
        Args:
            document (Document): Document object to process
            
        Returns:
            list: List of detected sensitive items
        """
        # Simulate processing delay
        time.sleep(4)
        
        # Similar to image processing but with page numbers
        results = self._process_image(document)
        
        # Add PDF-specific metadata
        for item in results:
            item['page'] = random.randint(1, 10)
            
        return results
    
    def _calculate_risk_level(self, sensitive_items):
        """
        Calculate risk level based on sensitive items detected
        
        Args:
            sensitive_items (list): List of detected sensitive items
            
        Returns:
            str: Risk level ('low', 'medium', 'high')
        """
        if not sensitive_items:
            return 'low'
        
        # Count high-risk items (documents, financial info)
        high_risk_count = sum(1 for item in sensitive_items 
                             if item['type'] in ['credit_card', 'passport', 'driver_license', 
                                                'social_security', 'bank_account'])
        
        # Count medium-risk items (contact info)
        medium_risk_count = sum(1 for item in sensitive_items 
                               if item['type'] in ['phone_number', 'email', 'address'])
        
        # Determine risk level based on counts
        if high_risk_count > 0:
            return 'high'
        elif medium_risk_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def _create_redacted_file(self, document, sensitive_items):
        """
        Create a redacted version of the document
        
        This is a placeholder implementation that mocks redaction.
        In a real implementation, this would apply actual redaction to the document.
        
        Args:
            document (Document): Document object to redact
            sensitive_items (list): List of detected sensitive items
            
        Returns:
            File: Redacted file
        """
        try:
            # For now, let's just create a copy of the original file
            # In a real implementation, this would apply redaction
            
            if document.file_type == 'image':
                # Create a placeholder redacted image
                # In a real implementation, this would apply actual redaction
                
                # Open the image file
                img = Image.open(document.file.path)
                draw = ImageDraw.Draw(img)
                
                # Draw rectangles over sensitive areas
                for item in sensitive_items:
                    if 'location' in item:
                        loc = item['location']
                        x = loc.get('x', 0)
                        y = loc.get('y', 0)
                        width = loc.get('width', 100)
                        height = loc.get('height', 20)
                        
                        # Draw a black rectangle
                        draw.rectangle(
                            [(x, y), (x + width, y + height)],
                            fill='black'
                        )
                
                # Save the redacted image
                img_temp = ContentFile(b'')
                img.save(img_temp, format='JPEG')
                img_temp.seek(0)
                
                return img_temp
            else:
                # For other types, just return a copy for now
                return document.file.file
                
        except Exception as e:
            print(f"Error creating redacted file: {str(e)}")
            return None 