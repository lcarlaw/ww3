"""
Before running this script, follow the instructions on this page
https://pythonhosted.org/PyDrive/quickstart.html to generate a client_secrets.json
file, and store this within the parent directory.

Script to automate the authentication process with Google Drive (i.e. each run of
uploader.py will no longer open a Google Chrome instance.)

This must be run a single time after the client_secrets.json file is downloaded. This
script will store and initialize the necessary items within credentials.txt.
"""
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def authorize_drive():
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = "client_secret.json"
    gauth.LoadCredentialsFile("credentials.txt")
    return GoogleDrive(gauth)

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("credentials.txt")
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
gauth.SaveCredentialsFile("credentials.txt")

authorize_drive()
