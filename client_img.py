import cv2
import os
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import socket

msgFromClient = "Howdy Server! I am sending the image to the Google Drive"
bytesToSend = msgFromClient.encode('utf-8')
print("Client is sending")
#serverAddress=('192.168.37.44', 2222) #change the ip address
serverAddress=('192.168.6.27', 2222)
bufferSize = 1024
UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

UDPClient.sendto(bytesToSend, serverAddress)

#Connection has been initiatedartiproject-77-6fd0f1a77701

# Google Drive credentials and settings
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
#SERVICE_ACCOUNT_FILE = 'artiproject-77-6fd0f1a77701.json'
#PARENT_FOLDER_ID = '1lNTUqqM_tDd3Qufyc3ktQANYI4pUx3B7'
PARENT_FOLDER_ID = '1O_LPqn7BzHnKewJpeemtq6881M7Apzg1'

def authenticate():
    """Authenticate using service account credentials."""
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def upload_photo(file_path):
    """Upload a photo file to Google Drive."""
    try:
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': os.path.basename(file_path),  # Use the filename as the desired name in Google Drive
            'parents': [PARENT_FOLDER_ID]  # Set the parent folder ID for the upload
        }

        media = MediaFileUpload(file_path, mimetype='image/jpeg', resumable=True)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f'File uploaded successfully! File ID: {file["id"]}')

        message = 'Uploaded_New_Data'
        message = message.encode('utf-8')
        UDPClient.sendto(message,serverAddress)

        print("Acknowledgment: Uploaded")
    except Exception as e:
        print(f'An error occurred while uploading: {e}')

def capture_images_and_upload(output_folder, interval_sec=60, num_images=None):
    """Capture images from a live video feed and upload them to Google Drive at regular intervals."""
    # Initialize the video capture device (default camera)
    cap = cv2.VideoCapture(0)  # Use the default camera (change to 1, 2, ... for different cameras)

    image_count = 0
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture frame from the camera.")
            break

        # Generate a unique filename based on current timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"
        filepath = os.path.join(output_folder, filename)

        # Save the captured frame as an image
        cv2.imwrite(filepath, frame)
        print(f"Saved image: {filename}")

        # Upload the captured image to Google Drive
        upload_photo(filepath)

        image_count += 1

        if num_images is not None and image_count >= num_images:
            print(f"Captured {num_images} images. Exiting...")
            break

        # Wait for the specified interval (in seconds) before capturing the next image
        time.sleep(interval_sec)

    # Release the video capture device and close any open windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Specify the output folder to save captured images
    output_folder = "captured_images"

    # Specify the capture interval in seconds (e.g., capture an image every 60 seconds)
    capture_interval_sec = 10

    # Specify the number of images to capture (None for indefinite capture)
    num_images_to_capture = None  # Set to a number (e.g., 10) to capture a specific number of images

    # Call the capture_images_and_upload function to start capturing images and uploading them to Google Drive
    capture_images_and_upload(output_folder, capture_interval_sec, num_images_to_capture)
