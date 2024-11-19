from ManageRecords import initialize_files, register_student,delete_student_record,delete_student_attendance
from Capture_Image import CaptureFaces
from Recognize import recognize_attendance
from Train_Image import train_images
from automail import send_email_with_yagmail  # Ensure this function is correctly implemented
import os



def main_menu():
    while True:
        print("[1] Check Camera")
        print("[2] Capture Faces")
        print("[3] Train Images")
        print("[4] Recognize & Attendance")
        print("[5] Auto Mail")
        print("[6] Delete Specific Student Record")
        print("[7] Delete Specific Student Attendance")
        print("[8] Quit")
        
        choice = input("Enter Choice: ")

        if choice == '1':
            print("Camera is working.")  # Placeholder for camera check
        elif choice == '2':
            CaptureFaces()  # Capture faces
        elif choice == '3':
            print("Training images...")
            train_images()  # Call the train_images function to train images
        elif choice == '4':
            recognize_attendance()  # Call the function to recognize attendance
        elif choice == '5':
            send_email_with_yagmail()  # Call the function to send email notifications
        elif choice == '6':
            delete_student_record()  # Delete a specific student record
        elif choice == '7':
            delete_student_attendance()
            break
        elif choice == '8':
            break
            print("Invalid choice. Please try again.")

if __name__ == "__main__":  # Create TrainingImage directory if it does not exist
    initialize_files()  # Initialize required files
    main_menu()  # Run the main menu
