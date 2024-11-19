import yagmail
import os

def send_email_with_yagmail(date, subject, receiver_email):
    sender_email = 'mlprojectproject@gmail.com'
    password = 'rhcv ibzh olqo sstu'  # Use app-specific password, not Gmail password
    
    # Construct the expected file path based on the provided date and subject
    csv_filename = f'{subject}_{date}.csv'
    csv_path = f'Face-Recognition-Attendance-System/FRAS/Attendance/{csv_filename}'
    
    # Check if the file exists
    if not os.path.isfile(csv_path):
        print(f'File not found: {csv_path}')
        return False  # Return False if file does not exist
    
    # Setup the yagmail SMTP client
    yag = yagmail.SMTP(user=sender_email, password=password)
    
    # Send the email with the CSV file attachment
    subject_line = f'Attendance Notification for {subject} on {date}'
    body = 'Please find the attached attendance file.'

    yag.send(to=receiver_email, subject=subject_line, contents=body, attachments=csv_path)
    print('Email sent successfully!')
    return True  # Return True if email sent successfully
