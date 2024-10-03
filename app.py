import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

app = Flask(__name__)

def get_drive_service():
    creds = Credentials(
        None,
        refresh_token=os.environ.get('GOOGLE_REFRESH_TOKEN'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    return build('drive', 'v3', credentials=creds)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file is provided
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if file:
            filename = secure_filename(file.filename)

            # Read file data into memory
            file_data = file.read()
            file_stream = io.BytesIO(file_data)

            # Upload to Google Drive
            drive_service = get_drive_service()
            file_metadata = {'name': filename}
            folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
            if folder_id:
                file_metadata['parents'] = [folder_id]
            media = MediaIoBaseUpload(file_stream, mimetype=file.mimetype, resumable=True)
            drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            return render_template('success.html', filename=filename)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
