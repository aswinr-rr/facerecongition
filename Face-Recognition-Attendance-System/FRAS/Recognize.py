import cv2
import torch
import os
import numpy as np
from facenet_pytorch import InceptionResnetV1, MTCNN
from datetime import datetime
import csv
import json,time

def get_current_class():
    try:
        # Load the class schedule from timetable.json
        with open("Face-Recognition-Attendance-System/FRAS/timetable.json", "r") as file:
            class_schedule = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Could not load timetable data.")
        return None, None

    # Get the current day of the week (e.g., 'Monday', 'Tuesday')
    current_day = datetime.now().strftime("%A")
    current_time = datetime.now().strftime("%H:%M")
    current_time_obj = datetime.strptime(current_time, "%H:%M")

    # Check if the current day exists in the timetable
    if current_day not in class_schedule:
        print(f"No classes scheduled for {current_day}.")
        return None, None

    # Retrieve today's schedule
    today_schedule = class_schedule[current_day]

    for subject, timings in today_schedule.items():
        start_time = timings['start_time']
        end_time = timings['end_time']

        # Convert start and end times to datetime objects for accurate comparison
        start_time_obj = datetime.strptime(start_time, "%H:%M")
        end_time_obj = datetime.strptime(end_time, "%H:%M")

        # If end_time is midnight, adjust it to the next day
        if end_time == "00:00":
            end_time_obj = end_time_obj.replace(day=start_time_obj.day + 1)

        # Check if the current time falls within the class's start and end times
        if start_time_obj <= current_time_obj < end_time_obj:
            return subject, f"{start_time}-{end_time}"

    return None, None  # No class is in session
# To store attendance in a session
marked_students = set()

# Load the model and MTCNN for face detection and embeddings
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
mtcnn = MTCNN(keep_all=True, device=device)

# Load embeddings and labels from the file
base_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
embeddings_folder = os.path.join(base_path, 'Embeddings')
attendance_folder = os.path.join(base_path, 'Attendance')  # Path to Attendance folder
model_save_path = os.path.join(embeddings_folder, 'embeddings.pt')

if os.path.exists(model_save_path):
    stored_embeddings, labels = torch.load(model_save_path)
else:
    print("Error: No trained embeddings found.")
    exit()

def is_attendance_marked(student_id):
    # Get today's date for checking attendance
    today = datetime.now().strftime('%Y-%m-%d')

    csv_filename = os.path.join(attendance_folder, f"Attendance_{today}.csv")
    if not os.path.exists(csv_filename):
        # If the attendance file doesn't exist, return False (no attendance marked yet)
        return False

    with open(csv_filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Assuming the attendance file has the format: [student_id, student_name, time]
            if len(row) >= 3 and row[0] == student_id and row[2].startswith(today):
                # Attendance already marked for this student today
                return True

    # If student_id not found for today, return False
    return False

def get_embedding(face_image):
    # Use MTCNN to detect the face and return the processed tensor
    face_tensor = mtcnn(face_image)
    
    # Check if MTCNN failed to detect a face
    if face_tensor is None:
        print("No face detected in the image.")
        return None
    
    # Ensure face_tensor has the correct shape [1, 3, 160, 160]
    # Remove any extra batch dimension if present
    face_tensor = face_tensor.squeeze()  # Remove all singleton dimensions if any exist
    
    # Now we check the shape of face_tensor and adjust if necessary
    if face_tensor.ndimension() == 3:  # Shape [3, 160, 160], add batch dimension
        face_tensor = face_tensor.unsqueeze(0)
    elif face_tensor.ndimension() == 4 and face_tensor.shape[0] > 1:
        # In case there are multiple detections, pick the first one for simplicity
        face_tensor = face_tensor[0].unsqueeze(0)
    
    # Move tensor to device for processing
    face_tensor = face_tensor.to(device)  # Shape should now be [1, 3, 160, 160]
    
    # Generate embedding from the face tensor using the model
    embedding = model(face_tensor).detach().cpu().numpy()
    return embedding

def compute_distances(embedding, stored_embeddings):
    distances = []
    for stored_embedding in stored_embeddings:
        dist = np.linalg.norm(embedding - stored_embedding)
        distances.append(dist)
    return np.array(distances)

def mark_attendance(rollno, name):
    # Extract the actual name by splitting the student ID and name (assuming "24_aswin")
    actual_name = name.split('_', 1)[-1]  # This will remove "24_" and keep "aswin"

    # Get the current date and subject to use in the filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    subject, time_slot = get_current_class()  # Get subject based on current time

    # Exit if no class is currently in session
    if not subject:
        print("No class in session at this time.")
        return

    # Format the filename to include only the subject and date
    csv_filename = os.path.join(
        attendance_folder,
        f"{subject}_{current_date}.csv"
    )

    # Check if attendance for this student has already been recorded
    if not os.path.exists(csv_filename):
        # Create the CSV file and add a header row if it doesn't exist
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Time"])  # Header

    # Get the current time
    current_time = datetime.now().strftime("%H:%M:%S")

    # Read the existing data to check for duplicates
    with open(csv_filename, mode='r') as file:
        reader = csv.reader(file)
        existing_entries = list(reader)

    # Check if the student has already been marked in this session
    if any(row[0] == rollno and row[1] == actual_name for row in existing_entries):
        print(f"Attendance for {actual_name} has already been recorded.")
        return

    # Write the attendance record
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([rollno, actual_name, current_time])  # Record with correct format

    print(f"Attendance recorded for {actual_name} in {subject} class at {current_time}.")


def recognize_attendance():
        # Open the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read frame from camera.")
            break

        # Display the camera feed
        cv2.imshow("Camera Feed", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the display window
    cap.release()
    cv2.destroyAllWindows()
    # cap = cv2.VideoCapture(0)
    # if not cap.isOpened():
    #     print("Error: Unable to access the camera.")
    #     return

    # last_marked_student = None
    # message_display_time = 2  # Duration in seconds to display the message
    # message_start_time = 0

    # while True:
    #     ret, frame = cap.read()
    #     if not ret:
    #         print("Error: Unable to read frame from camera.")
    #         break

    #     # Detect faces in the frame using MTCNN
    #     boxes, _ = mtcnn.detect(frame)

    #     if boxes is not None:
    #         for box in boxes:
    #             # Extract the face from the frame based on the bounding box
    #             face = frame[int(box[1]):int(box[3]), int(box[0]):int(box[2])]

    #             # Get the face embedding
    #             face_embedding = get_embedding(face)

    #             if face_embedding is not None:
    #                 distances = compute_distances(face_embedding, stored_embeddings)

    #                 if len(distances) == 0:
    #                     print("No distances available for comparison.")
    #                     continue

    #                 # Find the minimum distance (closest match)
    #                 min_index = np.argmin(distances)

    #                 # Ensure min_index is within bounds of the distances array
    #                 if min_index >= len(distances):
    #                     print(f"min_index {min_index} is out of bounds for distances array of size {len(distances)}")
    #                     continue

    #                 # Add threshold for recognition (e.g., distance < 0.6 means recognized)
    #                 if distances[min_index] < 0.6:
    #                     student_name = labels[min_index]
    #                     student_id = student_name.split('_')[0]  # Extract student ID from the name

    #                     print(f"Recognized: {student_name} with distance {distances[min_index]}")

    #                     # Check if attendance is already marked for the student
    #                     if not is_attendance_marked(student_id):
    #                         mark_attendance(student_id, student_name)
    #                         last_marked_student = student_name
    #                         message_start_time = time.time()  # Record the time when the message should appear
    #                     else:
    #                         print(f"Attendance for {student_name} has already been recorded.")
    #                 else:
    #                     print(f"Not recognized. Closest distance: {distances[min_index]}")
    #             else:
    #                 print("Error: Unable to compute embedding for the face.")
        
    #     # Display message if attendance has been marked recently
    #     if last_marked_student and (time.time() - message_start_time) < message_display_time:
    #         message = f"Attendance marked for {last_marked_student}"
    #         cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    #     else:
    #         last_marked_student = None  # Clear the message after display time

    #     cv2.imshow("Recognize & Attendance", frame)

    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # cap.release()
    # cv2.destroyAllWindows()


