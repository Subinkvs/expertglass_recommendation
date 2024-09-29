from django.urls import path
from .views import upload_image, generate_unique_image, extract_facial_features, get_explanation

urlpatterns = [
    path('upload-image/', upload_image, name='upload_image'),
    path('generate-unique/', generate_unique_image, name='generate_unique_image'),
    path('extract-features/', extract_facial_features, name='extract_facial_features'),
    path('get-explanation/', get_explanation, name='get_explanation'),
]
