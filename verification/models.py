from django.db import models
from django.utils import timezone
import json

class FaceEmbedding(models.Model):
    """Model to store face embeddings"""
    embedding_data = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Face Embedding {self.id} - {self.created_at}"
    
    def get_embedding(self):
        """Return the embedding as a list"""
        return self.embedding_data

class VerificationRecord(models.Model):
    """Model to store verification attempts"""
    known_image_path = models.CharField(max_length=255)
    new_image_path = models.CharField(max_length=255)
    is_verified = models.BooleanField()
    verification_date = models.DateTimeField(default=timezone.now)
    embedding = models.ForeignKey(FaceEmbedding, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Verification {self.id} - {'Success' if self.is_verified else 'Failed'} - {self.verification_date}"
