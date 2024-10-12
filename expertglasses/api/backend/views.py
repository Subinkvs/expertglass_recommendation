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

from expertglasses.expert_backend import ExpertEyeglassesRecommender  # Import your expert class
from rest_framework import status
from django.http import FileResponse
import io
from PIL import Image
import re
import requests



# Directory to temporarily save uploaded images
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploaded_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_uploaded_file(file):
    """ Helper function to save uploaded files to a temporary location """
    # Sanitize the file name to remove special characters
    safe_filename = re.sub(r'[^\w\-_\. ]', '_', file.name)
    img_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(img_path, "wb") as buffer:
        for chunk in file.chunks():
            buffer.write(chunk)
    
    return img_path
def download_image_from_url(url):
    """ Helper function to download image from a URL """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Ensure the request was successful

        # Extract filename from URL
        file_name = re.sub(r'[^\w\-_\. ]', '_', os.path.basename(url))
        img_path = os.path.join(UPLOAD_DIR, file_name)

            # Save the image in chunks
        with open(img_path, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    out_file.write(chunk)
        
        return img_path
    except Exception as e:
        raise Exception(f"Failed to download image from URL: {str(e)}")

@api_view(['POST'])
@parser_classes([MultiPartParser])
def generate_unique_image(request):
    file = request.FILES.get('file', None)
    file_url = request.data.get('file_url', None)
    lang = request.data.get('lang', 'en')

    if not file and not file_url:
        return Response({"error": "No file or URL provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if file:
            # If a file is uploaded, save it
            img_path = save_uploaded_file(file)
        elif file_url:
            # If a URL is provided, download the image
            img_path = download_image_from_url(file_url)
        
        # Initialize and generate the unique image
        ins = ExpertEyeglassesRecommender(img_path, lang=lang)
        generated_image = ins.generate_unique(show=False, block=False)
      
        try:
            os.remove(img_path)
        except OSError:
            pass  # Ignore cleanup errors

        # Convert the generated numpy image to a PIL Image
        pil_image = Image.fromarray(generated_image.astype('uint8'))

        # Save the PIL image to a BytesIO object
        img_io = io.BytesIO()
        pil_image.save(img_io, format='JPEG')
        img_io.seek(0)

        # Return the image as a FileResponse
        response = FileResponse(img_io, content_type='image/jpeg;')
        response['Content-Disposition'] = 'inline; filename="unique_eyeglass_frame.jpg"'
        return response

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_facial_features(request):
    file = request.FILES.get('file', None)
    file_url = request.data.get('file_url', None)
    lang = request.data.get('lang', 'en')

    if not file and not file_url:
        return Response({"error": "No file or URL provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if file:
            # If a file is uploaded, save it
            img_path = save_uploaded_file(file)
        elif file_url:
            # If a URL is provided, download the image
            img_path = download_image_from_url(file_url)
        
        recommender = ExpertEyeglassesRecommender(img_path, lang=lang)
        
        try:
            os.remove(img_path)
        except OSError:
            pass  # Ignore cleanup errors
       

        # Construct the facial features dictionary
        facial_features = {
        "face_shape": recommender._ExpertEyeglassesRecommender__get_faceshape(),  # Access private method via name mangling
        "hair_color": recommender._ExpertEyeglassesRecommender__get_hair(),
        "beard": recommender._ExpertEyeglassesRecommender__get_beard(),
        "jaw_type": recommender._ExpertEyeglassesRecommender__get_jawtype(),
        "nose": recommender._ExpertEyeglassesRecommender__get_nose(),
        "lips": recommender._ExpertEyeglassesRecommender__get_lips(),
        "skintone": recommender._ExpertEyeglassesRecommender__get_skintone(),
        "gender": recommender._ExpertEyeglassesRecommender__get_gender(),
    }

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Select the facial shape with the highest confidence value
    # highest_confidence_shape = max(facial_features["face_shape"], key=lambda x: x[0])
    # facial_features["face_shape"] = [highest_confidence_shape]  # Keep only the one with the highest confidence
    return Response({"facial_features": facial_features}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_explanation(request):
    
    file = request.FILES.get('file', None)
    file_url = request.data.get('file_url', None)
    lang = request.data.get('lang', 'en')

    if not file and not file_url:
        return Response({"error": "No file or URL provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if file:
            # If a file is uploaded, save it
            img_path = save_uploaded_file(file)
        elif file_url:
            # If a URL is provided, download the image
            img_path = download_image_from_url(file_url)
        
        recommender = ExpertEyeglassesRecommender(img_path, lang=lang)
        description = recommender.description
        
        try:
            os.remove(img_path)
        except OSError:
            pass  # Ignore cleanup errors
        
        organized_description = description.replace('\n', ' ').replace('\t', ' ').strip()
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"explanation": organized_description}, status=status.HTTP_200_OK)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def get_recommendations(request):
    file = request.FILES.get('file', None)
    file_url = request.data.get('file_url', None)
    lang = request.data.get('lang', 'en')

    if not file and not file_url:
        return Response({"error": "No file or URL provided."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if file:
            # If a file is uploaded, save it
            img_path = save_uploaded_file(file)
        elif file_url:
            # If a URL is provided, download the image
            img_path = download_image_from_url(file_url)
        
        # Initialize the ExpertEyeglassesRecommender with the image path and language
        ins = ExpertEyeglassesRecommender(img_path, lang=lang)
        
        try:
            os.remove(img_path)
        except OSError:
            pass  # Ignore cleanup errors

        # Call plot_recommendations to get the images as links
        recommended_images = ins.plot_recommendations(return_links=True)

        # Return the image links in the response
        return Response({
            'recommended_images': recommended_images
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)