# Import the ExpertEyeglassesRecommender class from the expert_backend module
from expert_backend import ExpertEyeglassesRecommender
import os

# Specify the path to the image
image_path = 'C:/Users/USER/Desktop/Images/Subin.jpg'

# Check if the image file exists
if not os.path.exists(image_path):
    print(f"Image file does not exist: {image_path}")
else:
    print(f"Image file found: {image_path}")

# Step 1: Initialize the class with the path to the image
ins = ExpertEyeglassesRecommender(image_path, lang='en')

# Step 4: Get an explanation of the system's recommendations
print(ins.description)

# Step 2: Get top 6 eyeglass recommendations using different strategies
try:
    ins.plot_recommendations(strategy='most_popular')
    ins.plot_recommendations(strategy='standart')
    ins.plot_recommendations(strategy='factorized')
    ins.plot_recommendations(strategy='factorized_plus')
    ins.plot_recommendations(strategy='color_only')
    ins.plot_recommendations(strategy='shape_only')
   
except Exception as e:
    print(f"Error during recommendation plotting: {e}")


# Step 5: Update the image and re-run the expert module
# Updating with a new local image (if needed)
ins.update_image(image_path)  # Already done at initialization

# Updating with an image from a URL
try:
    url = 'https://github.com/Defasium/expertglasses/blob/master/assets/gui.png?raw=true'
    ins.update_image(url)
    ins.expert_module()
except Exception as e:
    print(f"Error during updating image from URL: {e}")

# Step 6: Generate a unique eyeglass image using GANs
try:
    image = ins.generate_unique(show=True)
except Exception as e:
    print(f"Error during image generation: {e}")

