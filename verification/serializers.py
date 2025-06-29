from rest_framework import serializers
from .models import FaceEmbedding, VerificationRecord

class ImageUploadSerializer(serializers.Serializer):
    """Serializer for image upload/capture"""
    image = serializers.CharField(help_text="Base64 encoded image data")
    
class FaceVerificationSerializer(serializers.Serializer):
    """Serializer for face verification"""
    known_image = serializers.CharField(help_text="Base64 encoded known image")
    new_image = serializers.CharField(help_text="Base64 encoded new image to verify")

class FileUploadSerializer(serializers.Serializer):
    """Serializer for file upload"""
    file = serializers.FileField(help_text="Image file to upload")

class FaceEmbeddingSerializer(serializers.ModelSerializer):
    """Serializer for FaceEmbedding model"""
    class Meta:
        model = FaceEmbedding
        fields = ['id', 'embedding_data', 'created_at', 'updated_at']

class VerificationRecordSerializer(serializers.ModelSerializer):
    """Serializer for VerificationRecord model"""
    class Meta:
        model = VerificationRecord
        fields = ['id', 'known_image_path', 'new_image_path', 'is_verified', 'verification_date', 'embedding'] 