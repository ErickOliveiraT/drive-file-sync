from googleapiclient.discovery import build
from tinydb import TinyDB, where
import explorer
import drive
import files
import auth
import sys

remote_dir = '1l-sKq0MPteFHFQO_iDUYqLfCe-OcY31n'
local_dir = "C:/Users/erick/Desktop/teste/"

def main():
    #remote drive files database
    drive_files = TinyDB('drive_files.json')
    # print('Cleaning database')
    # drive_files.remove(where('id') > '')

    #start google drive service
    # print('Starting Google Drive Service')
    # creds = auth.get_credentials()
    # if not creds:
    #     print('Error while retrieving credentials')
    #     sys.exit(0)
    # service = build('drive', 'v3', credentials=creds)

    #list remote drive files
    # print('Checking remote files')
    # drive.list_files(remote_dir, service, drive_files)

    #build path for drive files
    # print('Building paths for remote files')
    # drive.build_paths(drive_files)

    #local files database
    local_files = TinyDB('local_files.json')
    # print('Cleaning database')
    # local_files.remove(where('id') > '')

    #list local files
    # print('Checking local files')
    # explorer.list_files(local_dir, local_files, local_dir)

    #compare local and remote drives
    files.compare(local_files, drive_files)





if __name__ == '__main__':
    main()