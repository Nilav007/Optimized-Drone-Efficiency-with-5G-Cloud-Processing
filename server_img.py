import socket
import os
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import io

#server is activating
bufferSize = 1024
msgfromServer = "Howdy CLient!! Please send the data"
ServerPort= 2222
ServerIP ='192.168.6.225'
bytesToSend = msgfromServer.encode('utf-8')
RPISocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RPISocket.bind((ServerIP, ServerPort))
print("Server is Listening")
mee, address = RPISocket.recvfrom(bufferSize)
mee = mee.decode('utf-8')
print(mee)
print("Client Address:", address[0])
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE ='service_account.json'
#FOLDER_ID = '1O_LPqn7BzHnKewJpeemtq6881M7Apzg1'  # Specify the ID of the folder to search for files
#FOLDER_ID='167khx_FPKukIJrouhOXYENhf9lYw9nzw'
FOLDER_ID = '1O_LPqn7BzHnKewJpeemtq6881M7Apzg1' 
# Global variable to store the IDs of downloaded files
downloaded_file_ids = set()

def authenticate():
    """Authenticate using service account credentials."""
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def download_images_in_folder(folder_id, destination_folder):
    print("Checking for new images...")
    """Download new images found in a specified folder in Google Drive."""
    try:
        global downloaded_file_ids

        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        # Create the destination folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)

        # Define query parameters to list image files (JPEG and PNG) in the specified folder
        query = f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png')"
        files = service.files().list(q=query, pageSize=1000, fields='files(id, name)').execute()

        if 'files' in files:
            new_files_found = False

            for file in files['files']:
                file_id = file['id']
                file_name = file['name']

                # Check if the file has already been downloaded
                if file_id not in downloaded_file_ids:
                    print("New file found")
                    new_files_found = True
                    print(f"Downloading file: {file_name} (ID: {file_id})")

                    # Create a request to download the file content
                    request = service.files().get_media(fileId=file_id)
                    destination_path = os.path.join(destination_folder, file_name)  # Set the destination path with unique filename
                    fh = io.FileIO(destination_path, 'wb')  # Open a file stream in binary write mode
                    downloader = MediaIoBaseDownload(fh, request)

                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(f'Download {int(status.progress() * 100)}%.')

                    print(f'File downloaded successfully to: {destination_path}')

                    # Add the downloaded file ID to the set
                    downloaded_file_ids.add(file_id)

            if not new_files_found:
                print("No new files were found.")

        else:
            print("No image files found in the specified folder.")

    except Exception as e:
        print(f'An error occurred while downloading: {e}')


if __name__ == "__main__":
    # Specify the destination folder where you want to save downloaded images
    destination_folder = 'captured_images'

    # Continuous execution loop
    while True:
        message, address = RPISocket.recvfrom(bufferSize)
        message = message.decode('utf-8')
        print("Acknowledgment:", message)
        if str(message) == "Uploaded_New_Data":
            # Call the function to download new images in the specified folder
            download_images_in_folder(FOLDER_ID, destination_folder)
        else:
            download_images_in_folder(FOLDER_ID, destination_folder)

        # Wait for 10 seconds before checking again (adjust as needed)
        time.sleep(10)  # Sleep for 10 seconds before the next iteration
