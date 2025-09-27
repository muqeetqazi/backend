"""
Enhanced user statistics tracking service
"""
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class UserStatsService:
    """
    Service for safely updating user statistics with proper error handling
    """
    
    @staticmethod
    @transaction.atomic
    def increment_documents_saved(user):
        """
        Safely increment documents saved counter
        """
        try:
            user.total_documents_saved += 1
            user.save(update_fields=['total_documents_saved'])
            logger.info(f"Incremented documents_saved for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to increment documents_saved for user {user.id}: {e}")
            raise
    
    @staticmethod
    @transaction.atomic
    def increment_documents_processed(user):
        """
        Safely increment documents processed counter
        """
        try:
            user.total_documents_processed += 1
            user.save(update_fields=['total_documents_processed'])
            logger.info(f"Incremented documents_processed for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to increment documents_processed for user {user.id}: {e}")
            raise
    
    @staticmethod
    @transaction.atomic
    def increment_documents_shared(user):
        """
        Safely increment documents shared counter
        """
        try:
            user.total_documents_shared += 1
            user.save(update_fields=['total_documents_shared'])
            logger.info(f"Incremented documents_shared for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to increment documents_shared for user {user.id}: {e}")
            raise
    
    @staticmethod
    @transaction.atomic
    def increment_sensitive_items_detected(user, count=1):
        """
        Safely increment sensitive items detected counter
        """
        try:
            if count < 0:
                raise ValueError("Count must be positive")
            user.total_sensitive_items_detected += count
            user.save(update_fields=['total_sensitive_items_detected'])
            logger.info(f"Incremented sensitive_items_detected by {count} for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to increment sensitive_items_detected for user {user.id}: {e}")
            raise
    
    @staticmethod
    @transaction.atomic
    def increment_non_detected_items(user, count=1):
        """
        Safely increment non-detected items counter
        """
        try:
            if count < 0:
                raise ValueError("Count must be positive")
            user.total_non_detected_items += count
            user.save(update_fields=['total_non_detected_items'])
            logger.info(f"Incremented non_detected_items by {count} for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to increment non_detected_items for user {user.id}: {e}")
            raise
    
    @staticmethod
    @transaction.atomic
    def update_stats_after_analysis(user, sensitive_count=0, non_sensitive_count=0):
        """
        Update multiple statistics after document analysis
        """
        try:
            if sensitive_count < 0 or non_sensitive_count < 0:
                raise ValueError("Counts must be non-negative")
            
            user.total_sensitive_items_detected += sensitive_count
            user.total_non_detected_items += non_sensitive_count
            
            user.save(update_fields=[
                'total_sensitive_items_detected',
                'total_non_detected_items'
            ])
            
            logger.info(f"Updated stats for user {user.id}: +{sensitive_count} sensitive, +{non_sensitive_count} non-sensitive")
        except Exception as e:
            logger.error(f"Failed to update stats for user {user.id}: {e}")
            raise
    
    @staticmethod
    def get_user_stats(user):
        """
        Get current user statistics
        """
        return {
            'total_documents_saved': user.total_documents_saved,
            'total_documents_processed': user.total_documents_processed,
            'total_documents_shared': user.total_documents_shared,
            'total_sensitive_items_detected': user.total_sensitive_items_detected,
            'total_non_detected_items': user.total_non_detected_items,
            'detection_accuracy': user.get_detection_accuracy()
        }
    
    @staticmethod
    def reset_user_stats(user):
        """
        Reset all user statistics to zero (for testing/admin purposes)
        """
        try:
            user.total_documents_saved = 0
            user.total_documents_processed = 0
            user.total_documents_shared = 0
            user.total_sensitive_items_detected = 0
            user.total_non_detected_items = 0
            
            user.save(update_fields=[
                'total_documents_saved',
                'total_documents_processed', 
                'total_documents_shared',
                'total_sensitive_items_detected',
                'total_non_detected_items'
            ])
            
            logger.info(f"Reset all stats for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to reset stats for user {user.id}: {e}")
            raise


# Convenience functions for backward compatibility
def increment_documents_saved(user):
    """Backward compatibility wrapper"""
    UserStatsService.increment_documents_saved(user)

def increment_documents_processed(user):
    """Backward compatibility wrapper"""
    UserStatsService.increment_documents_processed(user)

def increment_documents_shared(user):
    """Backward compatibility wrapper"""
    UserStatsService.increment_documents_shared(user)

def increment_sensitive_items_detected(user, count=1):
    """Backward compatibility wrapper"""
    UserStatsService.increment_sensitive_items_detected(user, count)

def increment_non_detected_items(user, count=1):
    """Backward compatibility wrapper"""
    UserStatsService.increment_non_detected_items(user, count)
