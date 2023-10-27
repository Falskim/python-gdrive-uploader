from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import os
import mimetypes

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
        
        gdrive_folder = self.drive.CreateFile({
            'title': dir_name,
            "mimeType": "application/vnd.google-apps.folder"
        })
        gdrive_folder.Upload()
        gdrive_folder_id = gdrive_folder['id']
        files = os.listdir(directory)

        for file in files:
            full_name = os.path.join(directory, file)
            print("Backing up {}".format(full_name))
            mime_type = mimetypes.guess_type(full_name)[0]
            if mime_type:
                f = self.drive.CreateFile({ 
                    'title': file,
                    "parents": [{ "id": gdrive_folder_id }],
                    'mimeType': mime_type})
                f.SetContentFile(full_name)
                f.Upload()
            else:
                print("Mime type for {} could not be determined. Skipping".format(file))
        
        print("Directory: {} backed up successfully".format(directory))
        
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("dir", help="Directory name to backup")

args = parser.parse_args()

gdrive_backup_creator = GoogleDriveBackupCreator()
gdrive_backup_creator.backup(args.dir)