from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.index, name='index'),
    path('capture/', views.capture_image, name='capture_image'),
    path('verify/', views.verify_faces, name='verify_faces'),
    path('upload/', views.upload_file, name='upload_file'),
    path('embeddings/', views.get_embeddings, name='get_embeddings'),
    
    path('api/capture/', api_views.capture_image_api, name='capture_image_api'),
    path('api/verify/', api_views.verify_faces_api, name='verify_faces_api'),
    path('api/upload/', api_views.upload_file_api, name='upload_file_api'),
    path('api/embeddings/', api_views.get_embeddings_api, name='get_embeddings_api'),
    path('api/records/', api_views.get_verification_records_api, name='get_verification_records_api'),
] 