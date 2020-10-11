from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import argparse

FOLDER = '1PdbtaISRJxTEyEpOzfvP-BmgfyjUuetX'

def upload_to_google_drive(file, short_name):
    file_list = drive.ListFile({'q':"'%s' in parents and trashed=False" %
                               (FOLDER)}).GetList()
    for file1 in file_list:
        if file1['title'] == short_name:
            id = file1['id']
    try:
        print("Updating an EXISTING FILE...")
        f = drive.CreateFile({'title': short_name, 'id':id})
        f.SetContentFile(file)
        f.Upload()
    except:
        print("This is a NEW FILE...")
        f = drive.CreateFile({'title': short_name, 'parents': [{'id': FOLDER}]})
        f.SetContentFile(file)
        f.Upload()

# Parse the passed arguments
parser = argparse.ArgumentParser()
parser.add_argument("files", help="List files to be uploaded.", nargs="+")

# Define the credentials folder
home_dir = os.path.expanduser("~")
credential_dir = os.path.join(home_dir, ".credentials")
if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
credential_path = os.path.join(credential_dir, "pydrive-credentials.json")

# Start authentication
gauth = GoogleAuth()
gauth.LoadCredentialsFile(credential_path)
if gauth.credentials is None:
    gauth.CommandLineAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile(credential_path)
drive = GoogleDrive(gauth)

# Upload the files
for f in parser.parse_args().files:
    short_name = f[f.rfind('/')+1:]
    upload_to_google_drive(f, short_name)
