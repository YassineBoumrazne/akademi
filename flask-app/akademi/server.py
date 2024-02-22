from flask import Flask, render_template, request, url_for, redirect, jsonify
import json
from flask_cors import CORS

from flask import send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
import os
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

userdata = 0

app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'processed_images', 'uploads')
app.config['FRAMES_FOLDER'] = os.path.join(os.getcwd(), 'processed_images', 'frames')
app.config['IMAGES_FOLDER'] = os.path.join(os.getcwd(), 'processed_images', 'images')


@app.route('/')
def home():
    return render_template('student-live.html')


@app.route('/new')
def new():
    print("Here we are")
    return render_template('view-insights2.html')
    # return jsonify(userdata)


@app.route('/getdata', methods=['GET'])
def getdata():
    print("here getedata")


    return jsonify(userdata)



def save_json_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def append_json_to_file(new_data, filename):
    try:
        with open(filename, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    existing_data.append(new_data)

    with open(filename, 'w') as file:
        json.dump(existing_data, file, indent=2)


@app.route('/result', methods=['GET', 'POST'])
def your_func():
    print(request.form)
    # print(type(request.form['data']))
    # print(json.loads(request.form))
    
    global userdata
    userdata = request.form
    print(userdata)
    file_name = f'api_server/ing_data/sceance_data.json'
    append_json_to_file(userdata, file_name)
    # print(request.method)
    # print(request.form)
    # if (request.method == 'POST'):
    #     print("here I am")
    # return render_template('result.html')
    return redirect(url_for('new'))



# Image proccessing



# Define the form for file upload
class UploadForm(FlaskForm):
    video = FileField('Upload Video', validators=[FileAllowed(['mp4', 'avi', 'mkv', 'mov'])])

def extract_frames(video_path, output_folder):
    if os.path.isfile(video_path):
        cam = cv2.VideoCapture(video_path)
        fps = cam.get(cv2.CAP_PROP_FPS)
        print(fps)

        total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
        target_frames = 10
        step = total_frames // target_frames

        for i in range(target_frames):
            frame_number = i * step
            cam.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cam.read()

            if ret:
                cv2.imwrite(os.path.join(output_folder, "{}.jpg".format(i)), frame)

        cam.release()
        cv2.destroyAllWindows()

def detect_faces(image_path, a, video_name):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    video_folder = os.path.join(app.config['IMAGES_FOLDER'], video_name)
    os.makedirs(video_folder, exist_ok=True)

    filepath = os.path.join(video_folder, f"frame_{a}_detected.png")
    cv2.imwrite(filepath, image)

    return filepath


def canny_filtre(image_path, video_name, frame_number):
    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply GaussianBlur to reduce noise and improve edge detection
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours on a black background with green color
    image_with_contours = image.copy()
    cv2.drawContours(image_with_contours, contours, -1, (0, 255, 0), 2)

    # Save the resulting image with contours
    output_folder = os.path.join("/processed_images/canny", video_name)
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"frame_{frame_number}_canny.png")
    cv2.imwrite(output_path, image_with_contours)

    print(output_path)

    return output_path




@app.route('/upload-video', methods=['GET', 'POST'])
def upload_video():
    form = UploadForm()

    if form.validate_on_submit():

        video = form.video.data
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)

        # Ensure the directory exists before saving the file
        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        video.save(video_path)

        frames_folder = os.path.join(app.config['FRAMES_FOLDER'], os.path.splitext(video.filename)[0])
        os.makedirs(frames_folder, exist_ok=True)

        extract_frames(video_path, frames_folder)

        return redirect(url_for('show_result', video_name=os.path.splitext(video.filename)[0]))

    return render_template('upload-video.html', form=form)

@app.route('/result/<video_name>')
def show_result(video_name):
    detected_image_paths = []
    for i in range(10):
        original_image_path = os.path.join(app.config['FRAMES_FOLDER'], video_name, f"{i}.jpg")
        detected_image_path = detect_faces(original_image_path, i, video_name)
        detected_image_paths.append(detected_image_path)

    return render_template('view-upload-result.html', video_name=video_name, detected_image_paths=detected_image_paths)


@app.route('/frames/<video_name>/<frame_name>')
def get_frame(video_name, frame_name):
    return send_from_directory(os.path.join(app.config['FRAMES_FOLDER'], video_name), frame_name)

@app.route('/detected_face/<video_name>/<int:frame_number>')
def show_detected_face(frame_number, video_name):
    detected_image_path = os.path.join(app.config['IMAGES_FOLDER'], video_name, f"frame_{frame_number}_detected.png")
    return send_from_directory(os.path.dirname(detected_image_path), os.path.basename(detected_image_path))

@app.route('/canny-filtre/<video_name>/<int:frame_number>')
def show_canny_filtre(video_name, frame_number):
    frame_name = f"{frame_number}.jpg"
    image_path = os.path.join(app.config['FRAMES_FOLDER'], video_name, frame_name)
    cannyOutput = canny_filtre(image_path, video_name, frame_number)
    return send_from_directory(os.path.dirname(cannyOutput), os.path.basename(cannyOutput))


@app.route('/insights')
def show():
    return render_template('view-upload-result.html')



# ----------------------


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)
