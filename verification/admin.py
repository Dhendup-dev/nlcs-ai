from django.contrib import admin
from .models import FaceEmbedding, VerificationRecord

@admin.register(FaceEmbedding)
class FaceEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('id',)

@admin.register(VerificationRecord)
class VerificationRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_verified', 'verification_date', 'embedding')
    list_filter = ('is_verified', 'verification_date')
    readonly_fields = ('verification_date',)
    search_fields = ('id', 'known_image_path', 'new_image_path')
