from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import os
import json
import base64
import uuid
from datetime import datetime
from .utils import verify_owner, get_face_embedding
from .models import FaceEmbedding, VerificationRecord

def index(request):
    """Render the main page"""
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def capture_image(request):
    """Handle image capture from camera"""
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        
        if not image_data:
            return JsonResponse({'error': 'No image data received'}, status=400)
        
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
        
        return JsonResponse({
            'success': True,
            'filename': filename,
            'filepath': filepath
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def verify_faces(request):
    """Handle face verification"""
    try:
        data = json.loads(request.body)
        known_image = data.get('known_image')
        new_image = data.get('new_image')
        
        if not known_image or not new_image:
            return JsonResponse({'error': 'Both images are required'}, status=400)
        
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
        VerificationRecord.objects.create(
            known_image_path=known_path,
            new_image_path=new_path,
            is_verified=is_verified,
            embedding=embedding_obj
        )
        
        # Clean up temporary files
        for temp_file in [known_path, new_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return JsonResponse({
            'success': True,
            'verified': is_verified,
            'embedding_saved': embedding is not None,
            'message': 'Verification successful!' if is_verified else 'Verification failed - faces do not match'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """Handle file uploads"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file part'}, status=400)
        
        file = request.FILES['file']
        if file.name == '':
            return JsonResponse({'error': 'No selected file'}, status=400)
        
        # Check file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        file_extension = file.name.rsplit('.', 1)[1].lower() if '.' in file.name else ''
        
        if file_extension not in allowed_extensions:
            return JsonResponse({'error': 'Invalid file type'}, status=400)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.name}"
        filepath = os.path.join(settings.UPLOAD_FOLDER, filename)
        
        # Save file
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        return JsonResponse({
            'success': True,
            'filename': filename,
            'filepath': filepath
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_embeddings(request):
    """Get the latest face embedding"""
    try:
        # Get the most recent embedding
        latest_embedding = FaceEmbedding.objects.order_by('-created_at').first()
        
        if latest_embedding:
            return JsonResponse({
                'success': True, 
                'embedding': latest_embedding.get_embedding()
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'No embedding found'
            })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
