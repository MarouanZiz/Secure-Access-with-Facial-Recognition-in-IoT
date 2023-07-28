import cv2
import face_recognition
import picamera
import numpy as np
import os
import requests
import json
from datetime import datetime
import time
import subprocess

# Function to load reference images and their corresponding encodings
def load_reference_images(data_folder):
    reference_encodings = []
    names = []
    for subdir in os.listdir(data_folder):
        subdir_path = os.path.join(data_folder, subdir)
        image_files = [f for f in os.listdir(subdir_path) if f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png")]
        for image_file in image_files:
            image_path = os.path.join(subdir_path, image_file)
            reference_image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(reference_image)
            if len(face_encodings) > 0:
                reference_encoding = face_encodings[0]
                reference_encodings.append(reference_encoding)
                names.append(subdir)
            else:
                print("No face detected in the image: {}".format(image_path))
    return reference_encodings, names

# Get a reference to the Raspberry Pi camera.
camera = picamera.PiCamera()
camera.resolution = (320, 240)

# Create a window to display the camera feed
cv2.namedWindow("Camera Feed", cv2.WINDOW_NORMAL)

# Specify the path to the folder containing the images
folder_path = "/home/pi/data"

# Load known face images and their encodings
known_faces = []
known_names = []

# Load reference images and their corresponding encodings
known_faces, known_names = load_reference_images(folder_path)

# Initialize some variables
face_locations = []
face_encodings = []
success = 0
prev_name = "Unknown"
email_sent = False

while True:
    print("Capturing image.")
    # Grab a single frame of video from the RPi camera as a numpy array
    output = np.empty((240, 320, 3), dtype=np.uint8)
    camera.capture(output, format="rgb")

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(output)
    # print("Found {} faces in image.".format(len(face_locations)))
    face_encodings = face_recognition.face_encodings(output, face_locations)

    # Display the camera feed with bounding boxes and labels
    frame = output.copy()
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare face encoding with the known face encodings
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        name = "Unknown"

        if True in matches:
            # Find the index of the matched encoding
            match_index = matches.index(True)
            name = known_names[match_index]
            color = (0, 255, 0)  # Green for known faces

            # Show the corresponding face image from the folder
            face_image_path = os.path.join(folder_path, name, f"{name}.jpg")
            face_image = cv2.imread(face_image_path)
            cv2.imshow(f"{name}", face_image)

        else:
            color = (0, 0, 255)  # Red for unknown faces

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # If the face is not recognized and the email has not been sent for this face, send the email
        if name == "Unknown" and prev_name == "Unknown" and not email_sent:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            image_filename = f"face_{timestamp.replace(':', '-')}.jpg"
            cv2.imwrite(image_filename, frame)
            subprocess.call(['python3', 'send_mail.py', name, image_filename])
            os.remove(image_filename)

            # Set the email_sent flag to True
            email_sent = True

            # Add the API-related code here
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            url = "http://192.168.43.245:8000/api/access-logs"
            image_path = ""
            if name == "Unknown":
                image_path = "null"
                success = 0
            else:
                image_path = "/home/pi/data/" + name + "/" + name + ".jpg"
                success = 1

            url1 = "http://192.168.43.245/open"
            payload1 = {}
            headers1 = {}
            response1 = requests.request("GET", url1, headers=headers1, data=payload1)
            print(response1.text)

            print(image_path)

            payload = json.dumps({
                "datetime": timestamp,
                "method": "face",
                "success": success,
                "image_path": image_path,
                "name": name
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)
            print("I see someone named {}!".format(name))
            # Reset the API request flag
            api_request_made = False


        # If the face is recognized, reset the email_sent flag
        # If the face is recognized, reset the email_sent flag
        if name != "Unknown" and not api_request_made:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            url = "http://192.168.43.245:8000/api/access-logs"
            image_path = "/home/pi/data/" + name + "/" + name + ".jpg"
            success = 1

            payload = json.dumps({
                "datetime": timestamp,
                "method": "face",
                "success": success,
                "image_path": image_path,
                "name": name
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)
            print("I see someone named {}!".format(name))

            # Set the API request flag to True
            api_request_made = True
            email_sent = False


        # Update the previous face name with the current name
        prev_name = name

        # Send the API request for recognized faces
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url = "http://192.168.43.245:8000/api/access-logs"
        image_path = ""
        if name == "Unknown":
            image_path = "null"
            success = 0
        else:
            image_path = "/home/pi/data/"+name+"/"+name+".jpg"
            success = 1

            url1 = "http://192.168.43.245/open"

            payload1 = {}
            headers1 = {}

            response1 = requests.request("GET", url1, headers=headers1, data=payload1)

            print(response1.text)

        print(image_path)

        payload = json.dumps({
            "datetime": timestamp,
            "method": "face",
            "success": success,
            "image_path": image_path,
            "name": name
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

    cv2.imshow("Camera Feed", frame)

    # Wait for a key event with a 1ms delay
    key = cv2.waitKey(1) & 0xFF

    # Check if the user pressed 'q' or 'x'
    if key == ord('q') or key == ord('x'):
        break

# Close the OpenCV window and release the camera resources
cv2.destroyAllWindows()
camera.close()