import sys
import os
import shutil
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from django.conf import settings

# Add the main directory to sys.path
main_directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(main_directory_path)

from expert_backend import ExpertEyeglassesRecommender  # Import your expert class
from rest_framework import status

# Directory to temporarily save uploaded images
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploaded_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_uploaded_file(file):
    """ Helper function to save uploaded files to a temporary location """
    img_path = os.path.join(UPLOAD_DIR, file.name)
    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return img_path

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_image(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    lang = request.data.get('lang', 'en')
    
    # Save uploaded image to a file
    img_path = save_uploaded_file(file)
    
    # Initialize the recommender
    try:
        recommender = ExpertEyeglassesRecommender(img_path, lang=lang)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"message": "Image uploaded successfully"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def generate_unique_image(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    lang = request.data.get('lang', 'en')
    show = request.data.get('show', True)
    
    # Save image temporarily
    img_path = save_uploaded_file(file)

    # Initialize recommender and generate unique image
    try:
        recommender = ExpertEyeglassesRecommender(img_path, lang=lang)
        unique_image = recommender.generate_unique(show=show)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"message": "Unique eyeglass frame generated", "unique_image": unique_image}, status=status.HTTP_200_OK)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_facial_features(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    lang = request.data.get('lang', 'en')
    
    # Save uploaded image
    img_path = save_uploaded_file(file)

    # Initialize recommender and extract facial features
    try:
        recommender = ExpertEyeglassesRecommender(img_path, lang=lang)
        facial_features = recommender.expert_module()
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"facial_features": facial_features}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_explanation(request):
    img_path = request.query_params.get('img_path')
    lang = request.query_params.get('lang', 'en')
    
    if not img_path or not os.path.exists(img_path):
        return Response({"error": "Image path not provided or does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize recommender and get explanation
    try:
        recommender = ExpertEyeglassesRecommender(img_path, lang=lang)
        description = recommender.description
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"explanation": description}, status=status.HTTP_200_OK)

