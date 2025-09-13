import os
import django
import random
from datetime import datetime, timedelta
from django.core.files.base import ContentFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models after setting up Django
from django.contrib.auth import get_user_model
from users.models import UserPreference
from documents.models import Document, DocumentScan, SensitiveInformation
from detection.models import DetectionModel, DetectionJob

User = get_user_model()

def create_users(num_users=5):
    """Create test users"""
    print(f"Creating {num_users} test users...")
    users = []
    
    for i in range(1, num_users+1):
        email = f"user{i}@example.com"
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            print(f"User {email} already exists, skipping...")
            continue
            
        user = User.objects.create_user(
            username=f"user{i}",
            email=email,
            password="testpassword123",
            first_name=f"Test{i}",
            last_name="User"
        )
        
        # Create user preferences
        UserPreference.objects.create(
            user=user,
            dark_mode=random.choice([True, False]),
            notifications_enabled=random.choice([True, False]),
            theme=random.choice(['light', 'dark', 'system']),
        )
        
        users.append(user)
        print(f"Created user: {email}")
    
    return users

def create_detection_models():
    """Create test detection models"""
    print("Creating detection models...")
    models = []
    
    model_types = ['yolo', 'ocr', 'transformer']
    model_names = [
        'YOLO v4 Tiny - Document Detection',
        'OCR Engine - Text Recognition',
        'BERT NLP - PII Detection',
        'Credit Card Detector',
        'ID Card Recognizer'
    ]
    
    for name in model_names:
        model_type = model_types[random.randint(0, len(model_types)-1)]
        version = f"1.{random.randint(0, 9)}.{random.randint(0, 9)}"
        
        # Check if model already exists
        if DetectionModel.objects.filter(name=name, version=version).exists():
            print(f"Model {name} v{version} already exists, skipping...")
            continue
            
        model = DetectionModel.objects.create(
            name=name,
            model_type=model_type,
            version=version,
            active=True
        )
        
        models.append(model)
        print(f"Created model: {name} v{version}")
    
    return models

def create_documents(users, num_docs_per_user=3):
    """Create test documents"""
    print(f"Creating {num_docs_per_user} documents per user...")
    documents = []
    
    doc_titles = [
        "Bank Statement", "Credit Card Photo", "Passport Scan", 
        "Driver's License", "Medical Record", "Tax Document", 
        "Insurance Card", "Resume", "Work Contract"
    ]
    
    doc_types = ['image', 'pdf', 'video']
    
    for user in users:
        for _ in range(num_docs_per_user):
            title = random.choice(doc_titles)
            file_type = random.choice(doc_types)
            
            # Create a dummy file content
            content = ContentFile(b"Test file content")
            content.name = f"{title.lower().replace(' ', '_')}.{file_type}"
            
            document = Document.objects.create(
                user=user,
                title=title,
                file=content,
                file_type=file_type,
                processed=random.choice([True, False])
            )
            
            documents.append(document)
            print(f"Created document: {title} for {user.email}")
    
    return documents

def create_document_scans(documents, detection_models):
    """Create test document scans"""
    print("Creating document scans...")
    scans = []
    
    sensitive_types = [
        'pii', 'credit_card', 'passport', 'driver_license', 
        'bank_account', 'social_security', 'phone_number', 
        'email', 'address', 'medical_record'
    ]
    
    risk_levels = ['low', 'medium', 'high']
    
    for document in documents:
        # Only create scans for processed documents
        if not document.processed:
            continue
            
        risk_level = random.choice(risk_levels)
        processing_time = random.uniform(0.5, 5.0)
        
        scan = DocumentScan.objects.create(
            document=document,
            risk_level=risk_level,
            processing_time=processing_time
        )
        
        # Create detection job
        job = DetectionJob.objects.create(
            document=document,
            status='completed',
            completed_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        
        # Add random models to the job
        num_models = random.randint(1, min(3, len(detection_models)))
        selected_models = random.sample(detection_models, num_models)
        job.models_used.set(selected_models)
        
        # Create sensitive information records
        num_sensitive_items = random.randint(0, 5)
        for _ in range(num_sensitive_items):
            sensitive_type = random.choice(sensitive_types)
            confidence = random.uniform(0.75, 0.99)
            
            location = {
                'x': random.randint(10, 500),
                'y': random.randint(10, 500),
                'width': random.randint(50, 200),
                'height': random.randint(20, 50)
            }
            
            SensitiveInformation.objects.create(
                scan=scan,
                type=sensitive_type,
                confidence=confidence,
                location=location,
                count=random.randint(1, 3),
                redacted=random.choice([True, False])
            )
        
        scans.append(scan)
        print(f"Created scan for document: {document.title}")
    
    return scans

def main():
    """Main function to generate test data"""
    print("Generating test data for Protected Vision backend...")
    
    # Create test data
    users = create_users()
    detection_models = create_detection_models()
    documents = create_documents(users)
    scans = create_document_scans(documents, detection_models)
    
    print("\nTest data generation complete!")
    print(f"Created {len(users)} users")
    print(f"Created {len(detection_models)} detection models")
    print(f"Created {len(documents)} documents")
    print(f"Created {len(scans)} document scans")
    
    print("\nLogin with any of these users:")
    for user in users:
        print(f"Email: {user.email}, Password: testpassword123")

if __name__ == "__main__":
    main() 