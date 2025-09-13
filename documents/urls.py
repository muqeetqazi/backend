from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, DocumentScanViewSet

# Setup the router
router = DefaultRouter()
router.register(r'', DocumentViewSet, basename='document')
router.register(r'scans', DocumentScanViewSet, basename='document-scan')

urlpatterns = [
    path('', include(router.urls)),
] 