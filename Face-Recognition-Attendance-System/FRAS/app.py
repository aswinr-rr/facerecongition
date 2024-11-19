from flask import Flask, render_template, request, redirect, url_for, session, flash
import Recognize  # Import the module for recognizing attendance
from Capture_Image import CaptureFaces
import Train_Image
import automail
import ManageRecords
import json,yagmail
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Hardcoded credentials for teacher login
USERNAME = 'teacher'
PASSWORD = 'password'

timetable_file = 'Face-Recognition-Attendance-System/FRAS/timetable.json'

# Function to load the timetable from JSON
def load_timetable():
    if os.path.exists(timetable_file):
        with open(timetable_file, 'r') as file:
            return json.load(file)
    return {}
# Route for student attendance recognition (Page 1)
@app.route('/')
def student_attendance():
    return render_template('student_attendance.html')

# Route to recognize attendance
@app.route('/recognize', methods=['POST'])
def recognize_attendance():
    Recognize.recognize_attendance()
    return redirect(url_for('student_attendance'))

# Route for teacher login (Page 1)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('teacher_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

# Route for the teacher dashboard (Page 2)
@app.route('/dashboard')
def teacher_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Route to capture faces
@app.route('/capture_faces', methods=['GET', 'POST'])
def capture_faces():
    if request.method == 'POST':
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        # Call your CaptureFaces function here
        # Make sure to modify CaptureFaces to take parameters
        CaptureFaces(student_id, student_name)
        return redirect('/')  # Redirect back to the dashboard or wherever you want

    return render_template('capture_face.html')

# Route to train images
@app.route('/train_images', methods=['POST'])
def train_images():
    Train_Image.train_images()
    flash("Training Successful!")
    return redirect(url_for('teacher_dashboard'))

@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    if request.method == 'POST':
        rollno = request.form['rollno']
        ManageRecords.delete_student_record(rollno)
        flash("Deletion Successful!")
    return render_template('delete_student.html')


@app.route('/delete_attendance', methods=['GET', 'POST'])
def delete_attendance():
    if request.method == 'POST':
        use_today = request.form.get('use_today')
        rollno = request.form.get('rollno')
        subject = request.form.get('subject')  # Get selected subject from form

        if use_today == "yes":
            from datetime import datetime
            today = datetime.now()
            month = today.strftime("%m")
            day = today.strftime("%d")
        else:
            month = request.form.get('month')
            day = request.form.get('day')

        # Call the delete function with subject, date, and roll number
        ManageRecords.delete_student_attendance(month, day, rollno, subject)
        flash("Attendance Removed!")

    return render_template('delete_attendance.html')


# Route to render the edit timetable form
@app.route('/edit_timetable', methods=['GET'])
def edit_timetable():
    timetable = load_timetable()
    return render_template('edit_timetable.html', timetable=timetable)

# Route to update the timetable
# Route to update the timetable
def save_timetable(timetable):
    try:
        with open(timetable_file, 'w') as file:
            json.dump(timetable, file, indent=4)
    except Exception as e:
        print(f"Error saving timetable: {e}")

# Route to update the timetable
@app.route('/update_timetable', methods=['POST'])
def update_timetable():
    day = request.form.get('day')
    subject = request.form.get('subject')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    if day and subject and start_time and end_time:
        timetable = load_timetable()

        # Ensure day exists in the timetable structure
        if day not in timetable:
            timetable[day] = {}

        # Check for any time conflicts on the specified day
        for existing_subject, times in timetable[day].items():
            if times['start_time'] == start_time and times['end_time'] == end_time:
                # If time matches, replace the subject
                del timetable[day][existing_subject]
                flash(f"Replaced existing subject '{existing_subject}' with '{subject}' for the specified time.", "success")
                break

        # Add or update the subject with new time
        timetable[day][subject] = {
            'start_time': start_time,
            'end_time': end_time
        }

        # Save the updated timetable to the JSON file
        save_timetable(timetable)
        flash("Timetable updated successfully!", "success")
    else:
        flash("All fields are required!", "error")

    return redirect(url_for('edit_timetable'))
@app.route('/send_email_form')
def send_email_form():
    return render_template('send_email.html')

# Dictionary to map names to emails
USER_EMAILS = {
    "aswin": "aswinforpc12@gmail.com",
    "Sheeba": "aswinforpc12@gmail.com",
    "Sheera" : "aswinforpc12@gmail.com",
    "Nadeera Bheevi":"aswinforpc12@gmail.com",
    "Fousiya" : "aswinforpc12@gmail.com"
}

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        # Extract form data
        date = request.form.get('date')
        subject = request.form.get('subject')
        receiver_name = request.form.get('receiver_name')
        receiver_email = request.form.get('receiver_email')

        # Determine the recipient email based on selection
        if receiver_name == "aswin":
            final_email = "aswinforpc12@gmail.com"
        elif receiver_name == "arjun":
            final_email = "aswinforpc12@gmail.com"  # Adjust if needed for different emails
        elif receiver_email:
            final_email = receiver_email
        else:
            flash("Please select or enter a valid email address.", "error")
            return redirect(url_for('send_email_form'))

        # Prepare file path based on date and subject
        filename = f"Face-Recognition-Attendance-System/FRAS/Attendance/{subject}_{date}.csv"

        # Set up Yagmail and send email
        sender_email = 'mlprojectproject@gmail.com'
        password = 'rhcv ibzh olqo sstu'
        yag = yagmail.SMTP(user=sender_email, password=password)
        subject = 'Attendance Notification'
        body = 'Please find the attendance file attached.'

        yag.send(to=final_email, subject=subject, contents=body, attachments=filename)
        flash('Email sent successfully!', 'success')
    except Exception as e:
        flash("An error occurred while sending the email. Please try again.", "error")
        print(f"Error: {e}")  # Log error for debugging

    return redirect(url_for('send_email_form'))

if __name__ == '__main__':
    app.run(debug=True)
