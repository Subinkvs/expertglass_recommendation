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
from io import BytesIO
import base64
import requests



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
    
    file = request.FILES['file']  # Handle the uploaded file
    lang = request.data.get('lang', 'en')
    
    img_path = save_uploaded_file(file)  # Save the uploaded file

    try:
        # Initialize and generate the unique image
        ins = ExpertEyeglassesRecommender(img_path, lang=lang)
        generated_image = ins.generate_unique(show=False, block=False)

        # Convert the generated numpy image to a PIL Image
        pil_image = Image.fromarray(generated_image.astype('uint8'))

        # Save the PIL image to a BytesIO object
        img_io = io.BytesIO()
        pil_image.save(img_io, format='JPEG')
        img_io.seek(0)  # Go back to the beginning of the file

        # Return the image as a FileResponse
        response = FileResponse(img_io, content_type='image/jpeg')
        response['Content-Disposition'] = 'inline; filename="unique_eyeglass_frame.jpg"'
        return response
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        eyeglasses_shape_vector, eyeglasses_color_vector = recommender.expert_module()  # Assuming this method returns the necessary vectors

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
    highest_confidence_shape = max(facial_features["face_shape"], key=lambda x: x[0])
    facial_features["face_shape"] = [highest_confidence_shape]  # Keep only the one with the highest confidence
    return Response({"facial_features": facial_features}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_explanation(request):
    
    if 'file' not in request.FILES:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    lang = request.data.get('lang','en')
    
    # Save uploaded image
    img_path = save_uploaded_file(file)
    if not img_path or not os.path.exists(img_path):
        return Response({"error": "Image path not provided or does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize recommender and get explanation
    try:
        recommender = ExpertEyeglassesRecommender(img_path, lang=lang)
        description = recommender.description
        
        organized_description = description.replace('\n', ' ').replace('\t', ' ').strip()
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"explanation": organized_description}, status=status.HTTP_200_OK)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def get_recommendations(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    lang = request.data.get('lang', 'en')

    img_path = save_uploaded_file(file)  # Save the uploaded file

    try:
        # Initialize the ExpertEyeglassesRecommender with the image path and language
        ins = ExpertEyeglassesRecommender(img_path, lang=lang)

        # Call plot_recommendations to get the images as links
        recommended_images = ins.plot_recommendations(return_links=True)

        # Convert recommended image links to base64
        base64_images = []
        for img_url in recommended_images:
            # Download the image
            response = requests.get(img_url)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                buffered = BytesIO()
                img.save(buffered, format="JPEG")  # Change format if needed
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                base64_images.append(f"data:image/jpeg;base64,{img_str}")

        # Return the base64 images in the response
        return Response({
            'recommended_images': base64_images
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)