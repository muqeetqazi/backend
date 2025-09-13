from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DetectionModelViewSet, DetectionJobViewSet, AnalysisViewSet

# Setup the router
router = DefaultRouter()
router.register(r'models', DetectionModelViewSet, basename='detection-model')
router.register(r'jobs', DetectionJobViewSet, basename='detection-job')
router.register(r'analyze', AnalysisViewSet, basename='analyze')

urlpatterns = [
    path('', include(router.urls)),
] 