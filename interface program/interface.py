from colorama import Cursor
import requests
import cv2
import face_recognition
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import datetime
import json
import subprocess



url = "http://192.168.43.245:8000"


payload = {}
headers = {}

# Folder path containing face image folders
data_path = "data"

# Create the main Tkinter window
window = tk.Tk()
window.title("Administration")
# Load the logo image
logo_image = tk.PhotoImage(file="R.png").subsample(5, 5)  # Scale the image down by a factor of 2


# Create a label to display the logo
logo_label = tk.Label(window, image=logo_image)
logo_label.pack(pady=10)  # Adjust the padding as needed
# Get the screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate the desired width and height for the window
window_width = 900
window_height = 800

# Calculate the x and y position for the Tkinter window to be centered
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

# Set the window size and position
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Initialize the camera
capture = cv2.VideoCapture(0)

# Function to check if a person already exists in the database
def person_exists(name):
    folder_path = os.path.join(data_path, name)
    if os.path.exists(folder_path):
        # Check if an image file exists inside the folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".jpg"):
                return True
    return False

# Function to check if a face already exists in the database
def face_exists(face_encoding):
    # Loop through the face image folders in the data path
    for folder_name in os.listdir(data_path):
        folder_path = os.path.join(data_path, folder_name)

        # Skip if the current item is not a directory
        if not os.path.isdir(folder_path):
            continue

        # Load the reference image from the folder
        reference_image = None
        reference_encoding = None

        for filename in os.listdir(folder_path):
            if filename.endswith(".jpg"):
                image_path = os.path.join(folder_path, filename)
                reference_image = face_recognition.load_image_file(image_path)
                reference_encoding = face_recognition.face_encodings(reference_image)[0]
                break  # Load only the first image for testing, you can remove this line to load all images

        # Check if a reference encoding is loaded
        if reference_encoding is None:
            print(f"No reference image found in folder: {folder_name}")
            continue

        # Compare face encoding with the reference encoding
        match = face_recognition.compare_faces([reference_encoding], face_encoding)
        if match[0]:
            return True

    return False

# Function to add a person to the database
def add_person():
    # Prompt for the person's name
    name = simpledialog.askstring("Add Person", "Enter the name of the person:")
    if not name:
        return

    # Check if the person already exists in the database
    if person_exists(name):
        messagebox.showinfo("Person Exists", f"The person '{name}' already exists in the database.")
        return

    # Capture frame from the camera
    ret, frame = capture.read()

    # Convert the frame to RGB format for compatibility with face_recognition library
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find faces in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Check if a face exists in the database
    if face_encodings:
        if face_exists(face_encodings[0]):
            messagebox.showinfo("Face Exists", "The face already exists in the database.")
            return

    # Create a folder for the person's images
    folder_path = os.path.join(data_path, name)
    os.makedirs(folder_path, exist_ok=True)

    # Save the captured frame as an image
    image_path = os.path.join(folder_path, f"{name}.jpg")
    cv2.imwrite(image_path, frame)

    messagebox.showinfo("Person Added", f"Person '{name}' added to the database.")
    # Define the command to call the other Python script
    command = ['python', 'send.py']

    # Run the command and capture the output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"Error executing the command: {e.output}")


# Function to perform face recognition and check if a person exists in the database
def check_person():
    # Capture frame from the camera
    ret, frame = capture.read()

    # Convert the frame to RGB format for compatibility with face_recognition library
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find faces in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Initialize recognized names and their corresponding face locations
    recognized_names = []
    recognized_face_locations = []

    # Loop through the face image folders in the data path
    for folder_name in os.listdir(data_path):
        folder_path = os.path.join(data_path, folder_name)

        # Skip if the current item is not a directory
        if not os.path.isdir(folder_path):
            continue

        # Load the reference image from the folder
        reference_image = None
        reference_encoding = None
        reference_name = folder_name

        for filename in os.listdir(folder_path):
            if filename.endswith(".jpg"):
                image_path = os.path.join(folder_path, filename)
                reference_image = face_recognition.load_image_file(image_path)
                reference_encoding = face_recognition.face_encodings(reference_image)[0]
                break  # Load only the first image for testing, you can remove this line to load all images

        # Check if a reference encoding is loaded
        if reference_encoding is None:
            print(f"No reference image found in folder: {folder_name}")
            continue

        # Perform face recognition
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare face encoding with the reference encoding
            match = face_recognition.compare_faces([reference_encoding], face_encoding)
            if match[0]:
                name = reference_name
                recognized_names.append(name)
                recognized_face_locations.append((top, right, bottom, left))

    # Draw bounding boxes and labels for recognized faces
    for (top, right, bottom, left) in face_locations:
        # Default name for unrecognized faces
        name = "Unknown"

        # Check if the face is recognized
        for (recognized_top, recognized_right, recognized_bottom, recognized_left), recognized_name in zip(
                recognized_face_locations, recognized_names):
            # Check if the face location matches
            if (top, right, bottom, left) == (recognized_top, recognized_right, recognized_bottom, recognized_left):
                name = recognized_name
                break

        # Draw bounding box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Put name on the bounding box
        cv2.putText(frame, name,(left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Insert the access request into the database
    if "Unknown" in recognized_names:
        print("Unkown.")
    # Display the frame with bounding boxes and labels
    cv2.imshow("Face Recognition", frame)

# Create the Treeview widget
tree = ttk.Treeview(window)

# Add columns to the Treeview
tree["columns"] = ('id', 'name', 'datetime', 'face', 'method')
# Configure column headers
tree.heading("#0", text="ID")
tree.heading("name", text="Name")
tree.heading("id", text="ID")
tree.heading("datetime", text="Datetime")
tree.heading("face", text="Face")
tree.heading("method", text="Method")

# # Set the column widths
# tree.column("#0", width=50)
# tree.column("name", width=250)
# tree.column("time", width=250)

# Configure the Treeview's style
style = ttk.Style()
style.configure("Treeview", font=("Arial", 12))
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

    # Set the initial value of the combobox to the first item
    
def list_rows():
    selected_index = combobox_options.index(selected_option.get())
    if selected_index == 0:  # Check by index
        response = requests.request("GET", url + "/api/access-logs?success=1", headers=headers, data=payload)
        data = json.loads(response.text)
    elif selected_index == 1:  # Check by index
        response = requests.request("GET", url + "/api/access-logs?success=0", headers=headers, data=payload)
        data = json.loads(response.text)
    else:
        messagebox.showerror("Error", "Invalid table selected.")
        return


    # Clear existing rows from the Treeview
    tree.delete(*tree.get_children())

    # Insert rows into the Treeview
    for row in data:
        tree.insert("", "end", text=['id', 'name', 'datetime', 'face', 'method',], values=(row['id'], row['name'], row['datetime'], row['image_path'], row['method']))

    # Adjust column widths
    for column in tree["columns"]:
        tree.column(column, width=200)  # Set a fixed width of 100 pixels

# Calculate the desired width for the buttons
button_width = 20
center_frame = tk.Frame(window)
center_frame.pack(expand=True)

# Create the "Check Person" button
check_button = tk.Button(center_frame, text="Check Person", command=check_person, bg="#3498db", fg="white", font=("Arial", 14), width=button_width)
check_button.pack(pady=10)


# Create the "Add Person" button
add_button = tk.Button(center_frame, text="Add Person", command=add_person, bg="#2ecc71", fg="white", font=("Arial", 14), width=button_width)
add_button.pack(pady=10)

# Create a list of options for the combobox
combobox_options = ["Successful Entries", "Denied Access Records"]

# Create a StringVar to hold the selected option
selected_option = tk.StringVar()

# Create the OptionMenu widget
option_menu = tk.OptionMenu(center_frame, selected_option, *combobox_options)
selected_option.set(combobox_options[0])  # Set the initial value to the first item
option_menu.config(width=25)
option_menu.pack(pady=10)

# Create a button to list the rows from the selected table
list_button = tk.Button(center_frame, text="List Logs", command=list_rows, bg="#f39c12", fg="white", font=("Arial", 14), width=10)
list_button.pack(pady=10)

# Configure the Treeview widget
tree.configure(show="headings")  # Hide the first empty column
tree.pack(padx=10, pady=(0, 20))  # Add bottom padding

# Create a list of options for the date combobox
date_options = [str(date.date()) for date in
                (datetime.datetime.now() - datetime.timedelta(days=x) for x in range((datetime.datetime.now() - datetime.datetime(2022, 1, 1)).days))]
default_date = datetime.date.today()
# Create the Date combobox
date_combobox = ttk.Combobox(center_frame, values=date_options, state="readonly", width=30)
date_combobox.set(str(default_date))  # Set the default date

# Configure the style for the Combobox
style = ttk.Style()
style.configure("TCombobox", padding=(10, 5), focuscolor="")  # Set the padding values and remove focus color

# Disable focus highlight
date_combobox.bind("<FocusIn>", lambda event: date_combobox.selection_clear())

date_combobox.pack()

def list_persons():
    selected_date = date_combobox.get()
    
    payload1 = json.dumps({
        "date": selected_date
    })
    
    headers2 = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url + "/api/access-logs/by-time", headers=headers2, data=payload1)
    
    data = json.loads(response.text)
    print(data)
    
    # Clear existing rows from the Treeview
    tree.delete(*tree.get_children())

    # Insert rows into the Treeview
    for row in data:
        tree.insert("", "end", text=['id', 'name', 'datetime', 'face', 'method'], values=(row['id'], row['name'], row['datetime'], row['image_path'], row['method']))


# Create the "Search" button
search_button = tk.Button(center_frame, text="Search", command=list_persons, bg="#f39c12", fg="white", font=("Arial", 14), width=button_width)
search_button.pack(pady=10)


window.mainloop()
