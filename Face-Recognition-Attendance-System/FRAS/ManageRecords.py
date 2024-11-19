import os
import csv
from datetime import datetime


def initialize_files():
    # Only create the student details file if it doesn't exist
    if not os.path.exists("Face-Recognition-Attendance-System/FRAS/studentdetails.csv"):
        with open("Face-Recognition-Attendance-System/FRAS/studentdetails.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name"])  # Write header
def get_current_class():
    class_schedule = {
        "9:00-9:15": "Python_Programming",
        "10:00-1:15": "Flutter"
    }

    current_time = datetime.now().strftime("%H:%M")
    for time_slot, subject in class_schedule.items():
        start_time, end_time = time_slot.split("-")
        
        if start_time <= current_time <= end_time:
            return subject, time_slot

    return None, None  # No class is in session



def register_student(student_id, student_name):
    student_details_file = "Face-Recognition-Attendance-System/FRAS/studentdetails.csv"
    with open(student_details_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([student_id, student_name])

# def record_attendance(roll_no, name):
#     # Get the current class based on the time
#     subject, time_slot = get_current_class()
    
#     # If no class is currently in session, exit the function
#     if not subject:
#         print("No class in session at this time.")
#         return

#     # Define the directory for attendance files
#     attendance_dir = "Face-Recognition-Attendance-System/FRAS/attendance"
#     if not os.path.exists(attendance_dir):
#         os.makedirs(attendance_dir)

#     # Format the date and time slot for the filename
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     formatted_time_slot = time_slot.replace(":", "")  # Remove colons for filename compatibility

#     # Create the filename with subject and time slot
#     attendance_file = os.path.join(attendance_dir, f"{subject}_{date_str}_{formatted_time_slot}.csv")

#     # Check if the record already exists to prevent duplicate entries
#     if os.path.exists(attendance_file):
#         with open(attendance_file, 'r') as f:
#             reader = csv.reader(f)
#             for row in reader:
#                 if row[0] == roll_no:
#                     print(f"Attendance for roll number {roll_no} is already recorded in {attendance_file}.")
#                     return

#     # Write the new attendance entry
#     with open(attendance_file, 'a', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([roll_no, name, datetime.now().strftime("%H:%M:%S")])
#     print(f"Recorded attendance for {name} in {subject} class.")



def delete_student_record(rollno):
    from main import main_menu

    student_details_file = os.path.join("Face-Recognition-Attendance-System", "FRAS", "studentdetails.csv")
    
    if not os.path.exists(student_details_file):
        print(f"Error: {student_details_file} does not exist.")
        return
    
    # Read the CSV file and filter out the record with the given rollno
    updated_records = []
    student_found = False

    with open(student_details_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 1 and row[0] != rollno:  # Assuming rollno is in the first column
                updated_records.append(row)
            else:
                student_found = True

    if not student_found:
        print(f"Roll number {rollno} not found in student records.")
        return

    # Write the updated records back to the CSV file
    with open(student_details_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_records)

    print(f"Record for roll number {rollno} deleted successfully.")

def delete_student_attendance(month, day, rollno, subject):
    attendance_file_name = f"{subject}_2024-{month}-{day}.csv"
    attendance_file_path = os.path.join("Face-Recognition-Attendance-System", "FRAS", "Attendance", attendance_file_name)

    if not os.path.exists(attendance_file_path):
        print(f"Error: {attendance_file_path} does not exist.")
        return

    updated_attendance = []
    attendance_found = False

    with open(attendance_file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 1 and row[0] != rollno:
                updated_attendance.append(row)
            else:
                attendance_found = True

    if not attendance_found:
        print(f"Roll number {rollno} not found in the attendance records for {month}-{day} in {subject}.")
        return

    with open(attendance_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_attendance)

    print(f"Attendance record for roll number {rollno} deleted successfully from {attendance_file_name}.")




