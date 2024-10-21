# Eyeglass recommendation

An eyeglasses recommendation system, based on an uploaded user image, utilizes machine learning and image analysis techniques to suggest suitable eyewear. The system is integrated with Django REST API to provide a seamless user experience. The process works as follows:

1.Image Upload: The user uploads a front-facing image of their face.

2.Face Detection and Feature Analysis: Using computer vision algorithms, the system detects the     user's facial features such as face shape, eye position, and symmetry.

3.Eyewear Matching: Based on the analysis, the system matches the user's facial attributes with     suitable eyeglass styles that complement their face shape, skin tone, and preferences.

4.Personalized Recommendations: The system provides recommendations, allowing the user to           virtually "try on" different eyeglasses, adjusting the fit to match their face.

5.Feedback and Selection: Users can explore various styles, save preferences, and receive recommendations based on trends or personal style choices.

### Prerequisites 

- conda installed
- python 3.6
- django 
- django restframework


## installations 

Clone the Repository
```sh
cd expertglasses
```

Install Dependencies

```sh
conda create -n expertglasses python=3.6
conda activate expertglasses
pip install -r requirements.txt
```

Run the GUI
```sh
python gui.py
```
#### GUI appears in matplotlib

### RESTAPI integration

Build django server
```sh
django-admin create myproject
python manage.py createapp appname
python manage.py runserver
```
server runs on http://127.0.0.1:8000/ 

