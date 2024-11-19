import cv2
import os
from ManageRecords import register_student  # Ensure this import is present

# captureimage.py
def CaptureFaces(student_id, student_name):
    # Remove input prompts; instead, use the passed parameters
    # student_id = input("Enter Student ID: ")

    # Specify the path to save images inside the FRAS/TrainingImage folder
    base_path = "Face-Recognition-Attendance-System/FRAS/TrainingImage"
    path = os.path.join(base_path, f"{student_id}_{student_name}")

    # Create the directory for the student's images if it doesn't exist
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"Directory created: {path}")
        except Exception as e:
            print(f"Error creating directory: {e}")
            return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read frame from camera.")
            break

        cv2.imshow("Capture Faces", frame)
        count += 1

        # Construct the filename and save the image
        image_filename = os.path.join(path, f"{student_name}_{count}.jpg")
        cv2.imwrite(image_filename, frame)
        print(f"Captured: {image_filename}")  # Debugging print statement

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if count >= 200:  # Capture up to 200 images
            break

    cap.release()
    cv2.destroyAllWindows()

    # Register student details after capturing images
    register_student(student_id, student_name)
    print(f"Registered {student_name} with ID {student_id}")

# Uncomment the next line to run the function directly
# CaptureFaces()
