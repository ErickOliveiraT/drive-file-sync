from googleapiclient.discovery import build
from tinydb import TinyDB, where
import drive
import auth
import sys

remote_dir = '1l-sKq0MPteFHFQO_iDUYqLfCe-OcY31n'

def main():
    #remote drive files database
    drive_files = TinyDB('drive_files.json')
    drive_files.remove(where('id') > '')

    #start google drive service
    creds = auth.get_credentials()
    if not creds:
        print('Error while retrieving credentials')
        sys.exit(0)
    service = build('drive', 'v3', credentials=creds)

    #list remote drive files
    drive.list_files(remote_dir, service, drive_files)

    #build path for drive files
    drive.build_paths(drive_files)








if __name__ == '__main__':
    main()