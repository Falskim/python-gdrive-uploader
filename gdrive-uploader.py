from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import os
import mimetypes

IGNORED_FILES = [
    '.gitignore'
]


class GoogleDriveBackupCreator():
    def __init__(self):
        gauth = GoogleAuth()
        # Try to load saved client credentials
        gauth.LoadCredentialsFile("cached_creds")
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile("cached_creds")

        self.drive = GoogleDrive(gauth)

    def backup(self, directory):
        dir_name = directory.split("/")[-1]

        dir_list = self.drive.ListFile(
            {'q': "'root' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"}).GetList()

        gdrive_dir_id = None
        for dir in dir_list:
            if dir['title'] == dir_name:
                gdrive_dir_id = dir['id']
                break

        # If Doesnt Exists, create the dir
        if not gdrive_dir_id:
            gdrive_dir = self.drive.CreateFile({
                'title': dir_name,
                "mimeType": "application/vnd.google-apps.folder"
            })
            gdrive_dir.Upload()
            gdrive_dir_id = gdrive_dir['id']

        files = os.listdir(directory)

        uploaded_files = []
        for file in files:
            if file in IGNORED_FILES:
                print(f"Skipping '{file}'")
                continue

            full_name = os.path.join(directory, file)
            print(f"Uploading '{full_name}'...")
            mime_type = mimetypes.guess_type(full_name)[0]
            if mime_type:
                f = self.drive.CreateFile({
                    'title': file,
                    "parents": [{"id": gdrive_dir_id}],
                    'mimeType': mime_type})
                f.SetContentFile(full_name)
                f.Upload()
            else:
                print("Mime type for {} could not be determined. Skipping".format(file))

            uploaded_files.append(full_name)
        print("Directory: {} backed up successfully".format(directory))

        return uploaded_files


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("dir", help="Directory name to backup")
parser.add_argument('-d', '--delete-file-after', action='store_const',
                    const=True, default=False, help="delete file after finish")

args = parser.parse_args()

gdrive_backup_creator = GoogleDriveBackupCreator()
uploaded_files = gdrive_backup_creator.backup(args.dir)

if args.delete_file_after:
    for file in uploaded_files:
        os.remove(file)
