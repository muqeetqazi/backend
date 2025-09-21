"""
Utility functions for updating user activity counters
"""
from django.contrib.auth import get_user_model

User = get_user_model()


def increment_documents_saved(user):
    """
    Increment the total documents saved counter for a user
    """
    user.total_documents_saved += 1
    user.save(update_fields=['total_documents_saved'])


def increment_documents_processed(user):
    """
    Increment the total documents processed counter for a user
    """
    user.total_documents_processed += 1
    user.save(update_fields=['total_documents_processed'])


def increment_documents_shared(user):
    """
    Increment the total documents shared counter for a user
    """
    user.total_documents_shared += 1
    user.save(update_fields=['total_documents_shared'])


def increment_sensitive_items_detected(user, count=1):
    """
    Increment the total sensitive items detected counter for a user
    """
    user.total_sensitive_items_detected += count
    user.save(update_fields=['total_sensitive_items_detected'])


def increment_non_detected_items(user, count=1):
    """
    Increment the total non-detected items counter for a user
    """
    user.total_non_detected_items += count
    user.save(update_fields=['total_non_detected_items'])


def update_user_stats_after_processing(user, sensitive_count, non_sensitive_count):
    """
    Update user statistics after document processing
    """
    user.total_documents_processed += 1
    user.total_sensitive_items_detected += sensitive_count
    user.total_non_detected_items += non_sensitive_count
    user.save(update_fields=[
        'total_documents_processed',
        'total_sensitive_items_detected', 
        'total_non_detected_items'
    ])
