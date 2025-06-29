from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from django.conf import settings
import os
import json
import base64
import uuid
from datetime import datetime
from .utils import verify_owner, get_face_embedding
from .models import FaceEmbedding, VerificationRecord
from .serializers import (
    ImageUploadSerializer, 
    FaceVerificationSerializer, 
    FileUploadSerializer,
    FaceEmbeddingSerializer,
    VerificationRecordSerializer
)

@api_view(['POST'])
@parser_classes([JSONParser])
def capture_image_api(request):
    """API endpoint for image capture from camera"""
    serializer = ImageUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        image_data = serializer.validated_data['image']
        
        # Remove data URL prefix
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"capture_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(settings.CAPTURES_FOLDER, filename)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        return Response({
            'success': True,
            'filename': filename,
            'filepath': filepath
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([JSONParser])
def verify_faces_api(request):
    """API endpoint for face verification"""
    serializer = FaceVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        known_image = serializer.validated_data['known_image']
        new_image = serializer.validated_data['new_image']
        
        # Save uploaded images temporarily
        known_path = os.path.join(settings.UPLOAD_FOLDER, 'known_temp.jpg')
        new_path = os.path.join(settings.UPLOAD_FOLDER, 'new_temp.jpg')
        
        # Decode and save known image
        if known_image.startswith('data:image'):
            known_image = known_image.split(',')[1]
        with open(known_path, 'wb') as f:
            f.write(base64.b64decode(known_image))
        
        # Decode and save new image
        if new_image.startswith('data:image'):
            new_image = new_image.split(',')[1]
        with open(new_path, 'wb') as f:
            f.write(base64.b64decode(new_image))
        
        # Perform verification
        is_verified = verify_owner(known_path, new_path)
        
        # Get face embedding if verified
        embedding = None
        embedding_obj = None
        if is_verified:
            embedding = get_face_embedding(new_path)
            if embedding:
                # Save embedding to database
                embedding_obj = FaceEmbedding.objects.create(embedding_data=embedding)
        
        # Create verification record
        verification_record = VerificationRecord.objects.create(
            known_image_path=known_path,
            new_image_path=new_path,
            is_verified=is_verified,
            embedding=embedding_obj
        )
        
        # Clean up temporary files
        for temp_file in [known_path, new_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return Response({
            'success': True,
            'verified': is_verified,
            'embedding_saved': embedding is not None,
            'verification_id': verification_record.id,
            'message': 'Verification successful!' if is_verified else 'Verification failed - faces do not match'
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file_api(request):
    """API endpoint for file uploads"""
    serializer = FileUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        file = serializer.validated_data['file']
        
        # Check file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        file_extension = file.name.rsplit('.', 1)[1].lower() if '.' in file.name else ''
        
        if file_extension not in allowed_extensions:
            return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.name}"
        filepath = os.path.join(settings.UPLOAD_FOLDER, filename)
        
        # Save file
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        return Response({
            'success': True,
            'filename': filename,
            'filepath': filepath
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_embeddings_api(request):
    """API endpoint to get the latest face embedding"""
    try:
        # Get the most recent embedding
        latest_embedding = FaceEmbedding.objects.order_by('-created_at').first()
        
        if latest_embedding:
            serializer = FaceEmbeddingSerializer(latest_embedding)
            return Response({
                'success': True, 
                'embedding': serializer.data
            })
        else:
            return Response({
                'success': False, 
                'message': 'No embedding found'
            })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_verification_records_api(request):
    """API endpoint to get verification records"""
    try:
        records = VerificationRecord.objects.order_by('-verification_date')[:10]  # Get last 10 records
        serializer = VerificationRecordSerializer(records, many=True)
        return Response({
            'success': True,
            'records': serializer.data
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 