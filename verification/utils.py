try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    print("Warning: deepface library not installed. Face verification will be disabled.")
    DEEPFACE_AVAILABLE = False
import json

def verify_owner(known_img_path, new_img_path):
    """Verify if two faces belong to the same person"""
    if not DEEPFACE_AVAILABLE:
        print("DeepFace not available - face verification disabled")
        return False
    
    try:
        result = DeepFace.verify(
            img1_path=known_img_path,
            img2_path=new_img_path,
            model_name="Facenet",  # Most accurate model
            detector_backend="retinaface",  # Best face detector
            enforce_detection=False  # Skip if no face found (for testing)
        )
        return result["verified"]  # Returns True/False
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_face_embedding(img_path):
    """Generate face embedding for the given image"""
    if not DEEPFACE_AVAILABLE:
        print("DeepFace not available - face embedding disabled")
        return None
    
    try:
        embedding = DeepFace.represent(
            img_path=img_path,
            model_name="Facenet"
        )
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None 