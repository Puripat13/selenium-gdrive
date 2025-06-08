
import os
import json
from pydrive2.auth import ServiceAccountCredentials
from pydrive2.drive import GoogleDrive

def upload_file_to_drive(filepath, folder_id):
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)

    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
    drive = GoogleDrive(creds)

    file_name = os.path.basename(filepath)
    file_drive = drive.CreateFile({"title": file_name, "parents": [{"id": folder_id}]})
    file_drive.SetContentFile(filepath)
    file_drive.Upload()
    print(f"✅ อัปโหลดไฟล์ {file_name} ไปยัง Google Drive สำเร็จ")
